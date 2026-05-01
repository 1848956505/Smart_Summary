"""
pipline_v8_3_2.py

两阶段数据合成管线，适配 configv8_3_2.py / prompts_v8_3_2.py。

默认只输出三个文件：
1. train_data_v8.3.2.json          最终可训练数据，只包含 QC 通过样本
2. train_data_v8.3.2.jsonl         JSONL 训练文件，只包含 QC 通过样本
3. quality_report_v8.3.2.json      质量报告

可选调试输出：
--save_rejected   额外保存 train_data_v8.3.2_rejected.json

核心逻辑：
1. 第一阶段只生成原始工作流水 input，允许使用 task_seeds；
2. 第二阶段只根据 instruction + input 生成 output，不再传入 task_seeds / role / scenario；
3. 生成后先清洗空的“待补充信息”栏目；
4. 增加实体一致性检查，重点拦截数字、型号、专有实体被改写的问题；
5. 默认剔除 QC 失败样本，最终训练集只保留 qc_passed=True 且 qc_issues=[] 的样本。
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from openai import OpenAI
from tqdm import tqdm

import configv8_3_2 as config
from prompts_v8_3_2 import INPUT_PROMPT, OUTPUT_PROMPT_MAP


PROMPT_VERSION = "v8.3.2"
DEFAULT_OUTPUT_DIR = str(Path(config.BASE_DIR) / "generated_data_v8_3_2")

random.seed(config.RANDOM_SEED)

STYLE_LABEL_MAP = {
    "from": "表格风格",   # 历史命名保持不变：from = 表格风格
    "list": "列表风格",
}

STYLE_SEED_OFFSET = {
    "from": 100_000,
    "list": 200_000,
}

FORBIDDEN_IN_INPUT_PATTERNS = [
    "请帮我整理",
    "生成周报",
    "风格要求",
    "当前周报风格",
    "请将下面",
    "请基于原始",
    "工作周报",
    "本周工作概览",
    "本周工作明细",
    "问题与风险",
    "下周计划",
]

FORBIDDEN_OUTPUT_PHRASES = [
    "显著提升",
    "全面优化",
    "重大突破",
    "圆满完成",
    "深度赋能",
    "形成机制",
    "有效保障",
    "请领导审阅",
    "祝周末愉快",
    "心得体会",
    "价值复盘",
    "思考与复盘",
    "高情商",
    "报喜不报忧",
    "危机公关",
    "失败原因分析",
]

TEMPLATE_TONE_PHRASES = [
    "本周主要围绕",
    "按计划推进",
    "聚焦于",
    "取得关键进展",
    "整体进度符合预期",
]

AUTO_SUGGESTION_PHRASES = [
    "制定方案",
    "建立机制",
    "完善机制",
    "优化机制",
    "引入缓存预热",
    "输出最佳实践",
    "沉淀方法论",
    "推动落地",
]

# 用于拦截“小米8 -> 红米8”这类实体改写。
DEVICE_ENTITY_PATTERN = re.compile(
    r"(?:iPhone\s*\d+[A-Za-z]*|"
    r"(?:小米|红米|华为|荣耀|OPPO|vivo|Pixel)\s*[A-Za-z0-9]+)",
    re.IGNORECASE,
)

# 只检查带单位的关键数值，降低“二十万 -> 20万”这类正常格式化带来的误杀。
NUMERIC_ENTITY_PATTERN = re.compile(
    r"(?<![A-Za-z0-9.])\d+(?:\.\d+)?\s*(?:%|秒|s|ms|分钟|小时|天|周|个月|MB|GB|并发|QPS)",
    re.IGNORECASE,
)


class SafeFormatDict(dict):
    """保留未匹配占位符，避免 prompt 中示例 JSON 的花括号报错。"""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def get_enabled_styles(styles_arg: Optional[List[str]] = None) -> List[str]:
    enabled_styles = styles_arg if styles_arg else getattr(config, "ENABLED_STYLES", list(OUTPUT_PROMPT_MAP.keys()))
    invalid_styles = [style for style in enabled_styles if style not in OUTPUT_PROMPT_MAP]
    if invalid_styles:
        raise ValueError(f"Unsupported style keys: {invalid_styles}; 可选值为 from/list")
    return enabled_styles


def init_client() -> OpenAI:
    if not getattr(config, "API_KEY", ""):
        raise ValueError(
            "API_KEY 为空。请先配置环境变量 DEEPSEEK_API_KEY，"
            "或在 configv8_3_2.py 中设置 API_KEY。"
        )
    return OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)


def load_task_seeds(path: str) -> Dict[str, List[str]]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("task_seeds.json 顶层必须是 dict: {role: [seed, ...]}")
    return {str(k): list(v) for k, v in data.items() if isinstance(v, list) and v}


TASK_SEEDS_DB = load_task_seeds(config.SEED_FILE)
FLAT_ROLES = list(TASK_SEEDS_DB.keys())


def extract_json_object(text: str) -> Dict[str, Any]:
    text = (text or "").strip()
    if not text:
        raise ValueError("模型返回为空")
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        obj = json.loads(text[start:end + 1])
    if not isinstance(obj, dict):
        raise ValueError("模型返回 JSON 顶层不是对象")
    return obj


def normalize_text(value: Any) -> str:
    return str(value or "").replace("\r\n", "\n").strip()


def build_input_prompt(
    role: str,
    scenario: str,
    task_seeds: str,
    routine_task: str,
    temporal_pattern: str,
) -> str:
    return INPUT_PROMPT.format_map(
        SafeFormatDict(
            role=role,
            scenario=scenario,
            task_seeds=task_seeds,
            routine_task=routine_task,
            temporal_pattern=temporal_pattern,
            name_mention_prob=config.NAME_MENTION_PROB,
            typo_noise_prob=config.TYPO_NOISE_PROB,
            emotion_noise_prob=config.EMOTION_NOISE_PROB,
            incomplete_info_prob=config.INCOMPLETE_INFO_PROB,
        )
    )


def build_output_prompt(style_name: str, instruction: str, input_text: str) -> str:
    return OUTPUT_PROMPT_MAP[style_name].format_map(
        SafeFormatDict(
            instruction=instruction,
            input_text=input_text,
        )
    )


def call_json(client: OpenAI, system_prompt: str, user_content: str, seed: int) -> Dict[str, Any]:
    response = client.chat.completions.create(
        model=config.MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        response_format={"type": "json_object"},
        temperature=config.TEMPERATURE,
        top_p=config.TOP_P,
        seed=seed,
    )
    return extract_json_object(response.choices[0].message.content)


def make_instruction(style_label: str, rng: random.Random) -> str:
    instruction_base = rng.choice(config.INSTRUCTION_POOL)
    return f"{instruction_base}（当前周报风格：{style_label}）"


def make_sample_id(style_name: str, sample_idx: int) -> str:
    return f"{PROMPT_VERSION}::{style_name}::{sample_idx}"


def contains_any(text: str, phrases: Iterable[str]) -> List[str]:
    return [p for p in phrases if p in text]


def _normal_entity(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def extract_device_entities(text: str) -> Set[str]:
    return {_normal_entity(m.group(0)) for m in DEVICE_ENTITY_PATTERN.finditer(text or "")}


def extract_numeric_entities(text: str) -> Set[str]:
    # 统一常见单位，便于比较 0.5秒 / 0.5s。
    values: Set[str] = set()
    for m in NUMERIC_ENTITY_PATTERN.finditer(text or ""):
        v = _normal_entity(m.group(0))
        v = v.replace("秒", "s").replace("分钟", "min").replace("小时", "h")
        values.add(v)
    return values


def int_to_simple_cn(num: int) -> str:
    """将 0~99 的整数转为常见中文数字，用于减少“六十多 -> 60%”误判。"""
    digits = "零一二三四五六七八九"
    if 0 <= num < 10:
        return digits[num]
    if num == 10:
        return "十"
    if 10 < num < 20:
        return "十" + digits[num % 10]
    if 20 <= num < 100:
        ten, one = divmod(num, 10)
        return digits[ten] + "十" + (digits[one] if one else "")
    return str(num)


def numeric_token_supported_by_input(token: str, input_text: str) -> bool:
    """判断 output 中的数值是否能在 input 中找到直接或弱等价依据。"""
    token_norm = _normal_entity(token)
    raw_numbers = re.findall(r"\d+(?:\.\d+)?", token_norm)
    if not raw_numbers:
        return True

    compact_input = _normal_entity(input_text)
    for raw_num in raw_numbers:
        # output 写 90%，input 写 90、90% 或 90了，都视为有依据。
        if raw_num in compact_input:
            continue

        # output 写 60%，input 写“百分之六十多”，也视为有依据。
        try:
            if "." not in raw_num:
                n = int(raw_num)
                if 0 <= n < 100:
                    cn = int_to_simple_cn(n)
                    if cn and (cn in compact_input or f"百分之{cn}" in compact_input):
                        continue
        except ValueError:
            pass

        return False
    return True


def detect_entity_consistency_issues(input_text: str, output_text: str) -> List[str]:
    """轻量实体一致性检查，重点拦截明确型号、关键数值被替换或新增。"""
    issues: List[str] = []

    input_devices = extract_device_entities(input_text)
    output_devices = extract_device_entities(output_text)
    added_devices = sorted(output_devices - input_devices)
    if added_devices:
        issues.append(f"output 出现 input 未提供的设备/型号实体: {added_devices[:5]}")

    input_numbers = extract_numeric_entities(input_text)
    unsupported_numbers: List[str] = []
    for token in sorted(extract_numeric_entities(output_text) - input_numbers):
        if not numeric_token_supported_by_input(token, input_text):
            unsupported_numbers.append(token)
    if unsupported_numbers:
        issues.append(f"output 出现 input 未提供的关键数值: {unsupported_numbers[:8]}")

    return issues


def _is_markdown_table_separator(line: str) -> bool:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return False
    return bool(re.fullmatch(r"\|\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)+\|", stripped))


def _is_supplement_header(line: str) -> bool:
    return bool(re.match(r"^##\s*待补充信息\s*$", line.strip()))


def _is_level2_header(line: str) -> bool:
    return bool(re.match(r"^##\s+", line.strip()))


def _block_is_empty_supplement(block_lines: List[str]) -> bool:
    meaningful: List[str] = []
    for line in block_lines:
        raw = line.strip()
        if not raw:
            continue
        if _is_markdown_table_separator(raw):
            continue
        # 去掉 Markdown 表格边框、项目符号和标点。
        cell_text = raw.strip("| ")
        if "待补充项" in cell_text and "原因" in cell_text:
            continue
        cell_text = re.sub(r"^[\-*+]\s*", "", cell_text).strip()
        cell_text = cell_text.strip("。；;，,| -")
        if cell_text:
            meaningful.append(cell_text)

    if not meaningful:
        return True

    empty_patterns = [
        r"^暂无明确待补充信息$",
        r"^暂无待补充信息$",
        r"^暂无明确记录$",
        r"^暂无$",
        r"^无$",
        r"^-$",
        r"^当前信息已覆盖主要事项$",
    ]
    for item in meaningful:
        normalized = re.sub(r"\s+", "", item)
        if not any(re.match(pattern, normalized) for pattern in empty_patterns):
            return False
    return True


def remove_empty_supplement_section(output_text: str) -> Tuple[str, bool]:
    """若“待补充信息”只是空占位，则删除整个栏目，降低模板味。"""
    lines = (output_text or "").splitlines()
    if not lines:
        return output_text, False

    new_lines: List[str] = []
    i = 0
    removed = False
    while i < len(lines):
        if _is_supplement_header(lines[i]):
            start = i
            end = i + 1
            while end < len(lines) and not _is_level2_header(lines[end]):
                end += 1
            if _block_is_empty_supplement(lines[start + 1:end]):
                # 删除前面多余空行，避免尾部留下多段空白。
                while new_lines and not new_lines[-1].strip():
                    new_lines.pop()
                removed = True
                i = end
                continue
        new_lines.append(lines[i])
        i += 1

    cleaned = "\n".join(new_lines).strip()
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned, removed

def _is_next_plan_header(line: str) -> bool:
    """
    识别“下周计划 / 后续计划 / 下周与后续计划”等计划栏目标题。
    兼容模型输出中的常见标题变体。
    """
    title = re.sub(r"\s+", "", line.strip())
    return bool(re.match(
        r"^##(下周计划|后续计划|下周/后续计划|下周与后续计划|下周及后续计划)$",
        title
    ))


def _block_is_empty_next_plan_table(block_lines: List[str]) -> bool:
    """
    识别空计划表：
    | 计划事项 | 关联工作 | 目标或处理方向 | 状态 |
    | :--- | :--- | :--- | :--- |
    | 暂无明确记录 | - | - | - |
    """
    empty_values = {"暂无明确记录", "暂无", "无", "-"}

    for line in block_lines:
        raw = line.strip()
        if not raw:
            continue
        if _is_markdown_table_separator(raw):
            continue
        if "计划事项" in raw and "关联工作" in raw:
            continue

        if raw.startswith("|"):
            cells = [cell.strip() for cell in raw.strip("|").split("|")]
            if not cells:
                continue
            first_cell = re.sub(r"\s+", "", cells[0])
            if first_cell in empty_values:
                return True

        compact = re.sub(r"\s+", "", raw)
        if compact in empty_values:
            return True

    return False


def simplify_empty_next_plan_section(output_text: str) -> Tuple[str, bool]:
    """
    将空的“下周计划/后续计划”表格改成一句话，减少模板占位感。
    """
    lines = (output_text or "").splitlines()
    if not lines:
        return output_text, False

    new_lines: List[str] = []
    i = 0
    changed = False

    while i < len(lines):
        if _is_next_plan_header(lines[i]):
            start = i
            end = i + 1
            while end < len(lines) and not _is_level2_header(lines[end]):
                end += 1

            block = lines[start + 1:end]
            if _block_is_empty_next_plan_table(block):
                while new_lines and not new_lines[-1].strip():
                    new_lines.pop()
                new_lines.append(lines[start].strip())
                new_lines.append("暂无明确记录。")
                changed = True
                i = end
                continue

        new_lines.append(lines[i])
        i += 1

    cleaned = "\n".join(new_lines).strip()
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned, changed



def clean_output_text(output_text: str) -> Tuple[str, List[str]]:
    actions: List[str] = []
    text = normalize_text(output_text)

    text, removed_supplement = remove_empty_supplement_section(text)
    if removed_supplement:
        actions.append("removed_empty_supplement_section")

    text, simplified_next_plan = simplify_empty_next_plan_section(text)
    if simplified_next_plan:
        actions.append("simplified_empty_next_plan_section")

    return text, actions


def validate_sample(sample: Dict[str, Any], style_name: str) -> Tuple[bool, List[str]]:
    issues: List[str] = []
    input_text = normalize_text(sample.get("input"))
    output_text = normalize_text(sample.get("output"))

    if len(input_text) < 20:
        issues.append("input 过短")
    if len(output_text) < 80:
        issues.append("output 过短")

    leaked = contains_any(input_text, FORBIDDEN_IN_INPUT_PATTERNS)
    if leaked:
        issues.append(f"input 疑似包含指令/结构化标题: {leaked[:3]}")

    forbidden = contains_any(output_text, FORBIDDEN_OUTPUT_PHRASES)
    if forbidden:
        issues.append(f"output 含禁用包装/结语词: {forbidden[:5]}")

    tone = contains_any(output_text, TEMPLATE_TONE_PHRASES)
    if tone:
        issues.append(f"output 含模板套话: {tone[:5]}")

    suggestions = contains_any(output_text, AUTO_SUGGESTION_PHRASES)
    if suggestions:
        issues.append(f"output 可能存在自动建议倾向: {suggestions[:5]}")

    issues.extend(detect_entity_consistency_issues(input_text, output_text))

    if style_name == "from":
        if "|" not in output_text or "| :---" not in output_text:
            issues.append("表格风格缺少 Markdown 表格结构")
    elif style_name == "list":
        if "| :---" in output_text or re.search(r"\n\|.+\|\n", output_text):
            issues.append("列表风格疑似混入 Markdown 表格")
        if "- " not in output_text and "* " not in output_text:
            issues.append("列表风格缺少项目符号列表")

    if "工作周报" not in output_text:
        issues.append("output 缺少工作周报标题")
    if "本周工作" not in output_text and "工作明细" not in output_text:
        issues.append("output 缺少工作内容相关栏目")

    return (len(issues) == 0), issues


def choose_context(style_name: str, sample_idx: int) -> Tuple[random.Random, int]:
    base_seed = config.RANDOM_SEED + STYLE_SEED_OFFSET.get(style_name, 0) + sample_idx
    return random.Random(base_seed), base_seed


def generate_input_only(
    client: OpenAI,
    role: str,
    scenario: str,
    seeds: List[str],
    routine_task: str,
    temporal_pattern: str,
    seed: int,
) -> str:
    task_seeds_str = "\n".join(f"- {seed_item}" for seed_item in seeds)
    prompt = build_input_prompt(
        role=role,
        scenario=scenario,
        task_seeds=task_seeds_str,
        routine_task=routine_task,
        temporal_pattern=temporal_pattern,
    )
    obj = call_json(
        client=client,
        system_prompt=prompt,
        user_content="请严格按 JSON 对象输出，仅包含 input 字段。",
        seed=seed,
    )
    input_text = normalize_text(obj.get("input"))
    if not input_text:
        raise ValueError("第一阶段未生成 input")
    return input_text


def generate_output_only(
    client: OpenAI,
    style_name: str,
    instruction: str,
    input_text: str,
    seed: int,
) -> str:
    prompt = build_output_prompt(style_name=style_name, instruction=instruction, input_text=input_text)
    obj = call_json(
        client=client,
        system_prompt=prompt,
        user_content="请严格按 JSON 对象输出，仅包含 output 字段。不得使用 input 之外的信息。",
        seed=seed,
    )
    output_text = normalize_text(obj.get("output"))
    if not output_text:
        raise ValueError("第二阶段未生成 output")
    return output_text


def generate_single_sample(style_name: str, sample_idx: int) -> Optional[Dict[str, Any]]:
    style_label = STYLE_LABEL_MAP.get(style_name, style_name)
    rng, base_seed = choose_context(style_name, sample_idx)
    client = init_client()
    sample_id = make_sample_id(style_name, sample_idx)

    last_sample: Optional[Dict[str, Any]] = None
    last_error: Optional[str] = None

    for attempt in range(config.MAX_RETRIES):
        try:
            role = rng.choice(FLAT_ROLES)
            scenario = rng.choice(config.SCENARIO_POOL)
            temporal_pattern = rng.choice(config.TEMPORAL_PATTERNS)
            instruction = make_instruction(style_label, rng)

            num_seeds = rng.randint(config.SEEDS_PER_SAMPLE_MIN, config.SEEDS_PER_SAMPLE_MAX)
            seeds = rng.sample(TASK_SEEDS_DB[role], min(num_seeds, len(TASK_SEEDS_DB[role])))
            routine_task = rng.choice(config.ROUTINE_TASKS) if rng.random() < config.ROUTINE_TASK_PROB else ""

            input_text = generate_input_only(
                client=client,
                role=role,
                scenario=scenario,
                seeds=seeds,
                routine_task=routine_task,
                temporal_pattern=temporal_pattern,
                seed=base_seed + attempt * 10 + 1,
            )

            output_text = generate_output_only(
                client=client,
                style_name=style_name,
                instruction=instruction,
                input_text=input_text,
                seed=base_seed + attempt * 10 + 2,
            )
            output_text, cleaning_actions = clean_output_text(output_text)

            sample: Dict[str, Any] = {
                "sample_id": sample_id,
                "instruction": instruction,
                "input": input_text,
                "output": output_text,
                "meta": {
                    "style": style_label,
                    "style_key": style_name,
                    "role": role,
                    "seeds": seeds,
                    "scenario": scenario,
                    "temporal_pattern": temporal_pattern,
                    "routine_task": routine_task,
                    "sample_idx": sample_idx,
                    "random_seed": base_seed,
                    "prompt_version": PROMPT_VERSION,
                    "two_stage_generation": True,
                    "output_stage_visible_fields": ["instruction", "input"],
                    "cleaning_actions": cleaning_actions,
                },
            }

            passed, issues = validate_sample(sample, style_name)
            sample["meta"]["qc_passed"] = passed
            sample["meta"]["qc_issues"] = issues
            last_sample = sample

            if passed:
                return sample

            last_error = f"QC failed: {issues}"
            print(f"\n质检未通过 [{style_name}] 样本 {sample_idx} 尝试 {attempt + 1}: {issues}")
            time.sleep(config.SLEEP_TIME)

        except Exception as exc:
            last_error = str(exc)
            print(f"\n出错 [{style_name}] 样本 {sample_idx} 尝试 {attempt + 1}: {exc}")
            time.sleep(config.SLEEP_TIME)

    if last_sample is not None:
        last_sample.setdefault("meta", {})["rejected_reason"] = last_error or "QC failed"
        return last_sample
    return None


def generate_all_samples(enabled_styles: List[str], samples_per_style: int) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    tasks: List[Tuple[str, int]] = []
    for style_name in enabled_styles:
        tasks.extend((style_name, idx) for idx in range(samples_per_style))

    rows: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []

    print(f"\n开始生成候选样本：{len(tasks)} 条")
    with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
        future_to_task = {
            executor.submit(generate_single_sample, style_name, idx): (style_name, idx)
            for style_name, idx in tasks
        }
        pbar = tqdm(total=len(tasks), desc="generate")
        for future in as_completed(future_to_task):
            style_name, idx = future_to_task[future]
            sample_id = make_sample_id(style_name, idx)
            try:
                sample = future.result()
                if sample is None:
                    rejected.append({"sample_id": sample_id, "style_key": style_name, "error": "生成失败"})
                else:
                    meta = sample.get("meta", {}) if isinstance(sample.get("meta"), dict) else {}
                    if meta.get("qc_passed") and not meta.get("qc_issues"):
                        rows.append(sample)
                    else:
                        rejected.append(sample)
            except Exception as exc:
                rejected.append({"sample_id": sample_id, "style_key": style_name, "error": str(exc)})
            finally:
                pbar.update(1)
        pbar.close()

    rng = random.Random(config.RANDOM_SEED)
    rng.shuffle(rows)
    return rows, rejected


def summarize_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    style_counts: Dict[str, int] = {}
    qc_passed = 0
    issue_counter: Dict[str, int] = {}
    cleaning_counter: Dict[str, int] = {}
    avg_input_len = 0.0
    avg_output_len = 0.0
    two_stage_count = 0

    for row in rows:
        meta = row.get("meta", {}) if isinstance(row.get("meta"), dict) else {}
        style = meta.get("style", row.get("style", "Unknown"))
        style_counts[style] = style_counts.get(style, 0) + 1
        if meta.get("qc_passed") and not meta.get("qc_issues"):
            qc_passed += 1
        if meta.get("two_stage_generation"):
            two_stage_count += 1
        for issue in meta.get("qc_issues", []) or []:
            key = str(issue).split(":")[0]
            issue_counter[key] = issue_counter.get(key, 0) + 1
        for action in meta.get("cleaning_actions", []) or []:
            cleaning_counter[str(action)] = cleaning_counter.get(str(action), 0) + 1
        avg_input_len += len(str(row.get("input", "")))
        avg_output_len += len(str(row.get("output", "")))

    count = len(rows)
    if count:
        avg_input_len = round(avg_input_len / count, 2)
        avg_output_len = round(avg_output_len / count, 2)

    return {
        "count": count,
        "style_counts": style_counts,
        "two_stage_count": two_stage_count,
        "two_stage_rate": round(two_stage_count / count, 4) if count else None,
        "qc_passed_count": qc_passed,
        "qc_passed_rate": round(qc_passed / count, 4) if count else None,
        "avg_input_len": avg_input_len,
        "avg_output_len": avg_output_len,
        "issue_counter": issue_counter,
        "cleaning_counter": cleaning_counter,
    }


def build_quality_report(rows: List[Dict[str, Any]], rejected: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(rows) + len(rejected)
    rejected_ids = [str(row.get("sample_id", "")) for row in rejected]
    return {
        "prompt_version": PROMPT_VERSION,
        "merge_policy": "clean_only_qc_passed_samples",
        "total_candidates": total,
        "clean_count": len(rows),
        "rejected_count": len(rejected),
        "clean_rate": round(len(rows) / total, 4) if total else None,
        "clean_summary": summarize_rows(rows),
        "rejected_summary": summarize_rows(rejected),
        "rejected_sample_ids": rejected_ids[:100],
    }


def write_outputs(
    rows: List[Dict[str, Any]],
    rejected: List[Dict[str, Any]],
    output_dir: str,
    save_rejected: bool = False,
) -> Dict[str, Any]:
    os.makedirs(output_dir, exist_ok=True)

    train_json = os.path.join(output_dir, f"train_data_{PROMPT_VERSION}.json")
    train_jsonl = os.path.join(output_dir, f"train_data_{PROMPT_VERSION}.jsonl")
    report_json = os.path.join(output_dir, f"quality_report_{PROMPT_VERSION}.json")

    with open(train_json, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    with open(train_jsonl, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    report = build_quality_report(rows, rejected)
    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    optional_files: Dict[str, str] = {}
    if save_rejected:
        rejected_json = os.path.join(output_dir, f"train_data_{PROMPT_VERSION}_rejected.json")
        with open(rejected_json, "w", encoding="utf-8") as f:
            json.dump(rejected, f, ensure_ascii=False, indent=2)
        optional_files["rejected_json"] = rejected_json

    return {
        "train_json": train_json,
        "train_jsonl": train_jsonl,
        "report_json": report_json,
        "optional_files": optional_files,
        "report": report,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SmartSummary-Pro v8.3.2 两阶段数据合成管线")
    parser.add_argument("--samples_per_style", type=int, default=config.SAMPLES_PER_STYLE)
    parser.add_argument("--styles", type=str, nargs="*", default=None, help="可选: from list")
    parser.add_argument("--output_dir", type=str, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--save_rejected", action="store_true", help="调试用：额外保存 QC 失败样本")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    enabled_styles = get_enabled_styles(args.styles)

    print(
        f"开始两阶段数据合成任务 | 目标：{len(enabled_styles)} 种风格 x "
        f"{args.samples_per_style} 条"
    )
    print(f"   启用风格：{', '.join(enabled_styles)}")
    print(f"   配置: 模型={config.MODEL_NAME}, 温度={config.TEMPERATURE}, Top-p={config.TOP_P}, 随机种子={config.RANDOM_SEED}")
    print(f"   并行度: {config.NUM_WORKERS} 个线程")
    print(f"   输出目录: {args.output_dir}")
    print("   生成逻辑: 第一阶段生成 input；第二阶段仅根据 instruction + input 生成 output")
    print("   清洗规则: 省略空的待补充信息栏目；简化空的下周/后续计划表格；检查设备/型号和关键数值一致性")

    rows, rejected = generate_all_samples(enabled_styles=enabled_styles, samples_per_style=args.samples_per_style)
    paths = write_outputs(rows=rows, rejected=rejected, output_dir=args.output_dir, save_rejected=args.save_rejected)

    print("\n所有数据处理完毕！")
    print(f"最终训练 JSON : {paths['train_json']}")
    print(f"最终训练 JSONL: {paths['train_jsonl']}")
    print(f"质量报告: {paths['report_json']}")
    if paths["optional_files"]:
        for name, path in paths["optional_files"].items():
            print(f"{name}: {path}")
    print(json.dumps(paths["report"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
