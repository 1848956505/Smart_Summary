"""
pipline_v8_3_1.py

适配 prompts_v8_3_1.py / configv8_3_1.py 的数据合成管线。

核心变化：
1. prompt 不再注入 instruction，instruction 只作为最终训练样本字段保存；
2. meta.style 统一保存为“表格风格 / 列表风格”，同时保留 style_key；
3. 增加样本级校验：JSON 解析、input 指令泄漏、表格/列表格式、包装词、自动建议倾向；
4. 支持断点续跑，避免重复写入；
5. 生成完成后自动合并两个风格文件，并输出质量检查报告。
"""

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

import configv8_3_1 as config


random.seed(config.RANDOM_SEED)


PROMPT_MAP = {
    "from": config.FROM_PROMPT,   # 历史命名保持不变：from = 表格风格
    "list": config.LIST_PROMPT,
}

STYLE_LABEL_MAP = {
    "from": "表格风格",
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
]


class SafeFormatDict(dict):
    """保留未匹配占位符，避免 prompt 中示例 JSON 的花括号报错。"""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def get_enabled_styles() -> List[str]:
    enabled_styles = getattr(config, "ENABLED_STYLES", list(PROMPT_MAP.keys()))
    invalid_styles = [style for style in enabled_styles if style not in PROMPT_MAP]
    if invalid_styles:
        raise ValueError(f"Unsupported style keys in ENABLED_STYLES: {invalid_styles}")
    return enabled_styles


def init_client() -> OpenAI:
    if not getattr(config, "API_KEY", ""):
        raise ValueError(
            "API_KEY 为空。请先配置环境变量 DEEPSEEK_API_KEY，"
            "或在 configv8_3_1.py 中设置 API_KEY。"
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


def build_prompt(
    prompt_template: str,
    role: str,
    scenario: str,
    task_seeds: str,
    routine_task: str,
    temporal_pattern: str,
) -> str:
    """
    v8.3.1 的 prompt 内部已经定义了 input/output 两阶段任务。
    instruction 不再注入 prompt，避免生成的原始 input 泄漏任务指令。
    """
    return prompt_template.format_map(
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


def extract_json_object(text: str) -> Dict[str, Any]:
    """兼容模型偶尔返回代码块或 JSON 前后带文本的情况。"""
    text = (text or "").strip()
    if not text:
        raise ValueError("模型返回为空")

    # 去掉常见 markdown 代码块壳
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


def make_instruction(style_label: str, rng: random.Random) -> str:
    instruction_base = rng.choice(config.INSTRUCTION_POOL)
    return f"{instruction_base}（当前周报风格：{style_label}）"


def make_sample_id(style_name: str, sample_idx: int) -> str:
    return f"v8.3.1::{style_name}::{sample_idx}"


def read_existing_sample_ids(path: str) -> Set[str]:
    existing: Set[str] = set()
    if not os.path.exists(path):
        return existing
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            sample_id = obj.get("sample_id")
            if sample_id is not None:
                existing.add(str(sample_id))
    return existing


def contains_any(text: str, phrases: Iterable[str]) -> List[str]:
    return [p for p in phrases if p in text]


def validate_sample(sample: Dict[str, Any], style_name: str) -> Tuple[bool, List[str]]:
    """
    轻量质量检查：不是替代人工审核，而是过滤明显跑偏样本。
    返回 (是否通过, 问题列表)。
    """
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
        # 这里不直接判死刑，因为有些输入中可能真的提到“制定方案”。交给人工复核。
        issues.append(f"output 可能存在自动建议倾向: {suggestions[:5]}")

    if style_name == "from":
        if "|" not in output_text or "| :---" not in output_text:
            issues.append("表格风格缺少 Markdown 表格结构")
    elif style_name == "list":
        if "| :---" in output_text or re.search(r"\n\|.+\|\n", output_text):
            issues.append("列表风格疑似混入 Markdown 表格")
        if "- " not in output_text and "* " not in output_text:
            issues.append("列表风格缺少项目符号列表")

    # 必备栏目检查：保持宽松，允许非标准样本，但至少应有工作周报和明细/概览之一。
    if "工作周报" not in output_text:
        issues.append("output 缺少工作周报标题")
    if "本周工作" not in output_text and "工作明细" not in output_text:
        issues.append("output 缺少工作内容相关栏目")

    # 严重问题才失败；自动建议和轻微套话保留为 warning，不直接丢弃，方便后续人工看。
    hard_fail_keywords = [
        "input 过短",
        "output 过短",
        "input 疑似包含指令/结构化标题",
        "表格风格缺少 Markdown 表格结构",
        "列表风格疑似混入 Markdown 表格",
        "列表风格缺少项目符号列表",
    ]
    hard_failed = any(any(k in issue for k in hard_fail_keywords) for issue in issues)
    return (not hard_failed), issues


def generate_single_sample(
    style_name: str,
    prompt_template: str,
    sample_idx: int,
    strict_validation: bool = True,
) -> Optional[Dict[str, Any]]:
    style_label = STYLE_LABEL_MAP.get(style_name, style_name)
    base_seed = config.RANDOM_SEED + STYLE_SEED_OFFSET.get(style_name, 0) + sample_idx
    rng = random.Random(base_seed)
    client = init_client()

    sample_id = make_sample_id(style_name, sample_idx)

    for attempt in range(config.MAX_RETRIES):
        try:
            role = rng.choice(FLAT_ROLES)
            scenario = rng.choice(config.SCENARIO_POOL)
            temporal_pattern = rng.choice(config.TEMPORAL_PATTERNS)
            instruction = make_instruction(style_label, rng)

            num_seeds = rng.randint(config.SEEDS_PER_SAMPLE_MIN, config.SEEDS_PER_SAMPLE_MAX)
            seeds = rng.sample(TASK_SEEDS_DB[role], min(num_seeds, len(TASK_SEEDS_DB[role])))
            task_seeds_str = "\n".join(f"- {seed}" for seed in seeds)

            routine_task = rng.choice(config.ROUTINE_TASKS) if rng.random() < config.ROUTINE_TASK_PROB else ""

            formatted_prompt = build_prompt(
                prompt_template=prompt_template,
                role=role,
                scenario=scenario,
                task_seeds=task_seeds_str,
                routine_task=routine_task,
                temporal_pattern=temporal_pattern,
            )

            response = client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": formatted_prompt},
                    {
                        "role": "user",
                        "content": (
                            "请严格按 JSON 对象输出，仅包含 input 和 output 两个字段。"
                            "input 不得包含任务指令或周报标题。"
                        ),
                    },
                ],
                response_format={"type": "json_object"},
                temperature=config.TEMPERATURE,
                top_p=config.TOP_P,
                seed=base_seed + attempt,
            )

            res_json = extract_json_object(response.choices[0].message.content)
            input_text = normalize_text(res_json.get("input"))
            output_text = normalize_text(res_json.get("output"))

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
                    "prompt_version": "v8.3.1",
                },
            }

            passed, issues = validate_sample(sample, style_name)
            sample["meta"]["qc_passed"] = passed
            sample["meta"]["qc_issues"] = issues

            if strict_validation and not passed:
                raise ValueError(f"样本质检未通过: {issues}")

            return sample

        except Exception as exc:
            print(f"\n出错 [{style_name}] 样本 {sample_idx} 尝试 {attempt + 1}: {exc}")
            time.sleep(config.SLEEP_TIME)

    return None


def generate_style_samples(
    style_name: str,
    prompt_template: str,
    total_samples: int,
    resume: bool = True,
    strict_validation: bool = True,
) -> int:
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    output_file = os.path.join(
        config.OUTPUT_DIR,
        config.OUTPUT_FILE_PATTERN.format(style=style_name),
    )
    error_file = output_file.replace(".jsonl", "_errors.jsonl")

    existing_ids = read_existing_sample_ids(output_file) if resume else set()
    target_indices = [
        idx for idx in range(total_samples)
        if make_sample_id(style_name, idx) not in existing_ids
    ]

    print(f"\n正在生成 {style_name} 风格数据 -> {output_file}")
    print(f"   目标数量: {total_samples} | 已存在: {len(existing_ids)} | 待生成: {len(target_indices)}")
    print(f"   使用 {config.NUM_WORKERS} 个线程并行处理...")

    success_count = 0
    pbar = tqdm(total=len(target_indices), desc=style_name)

    with open(output_file, "a", encoding="utf-8") as f, open(error_file, "a", encoding="utf-8") as ef:
        with ThreadPoolExecutor(max_workers=config.NUM_WORKERS) as executor:
            future_to_idx = {
                executor.submit(
                    generate_single_sample,
                    style_name,
                    prompt_template,
                    idx,
                    strict_validation,
                ): idx
                for idx in target_indices
            }

            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                sample_id = make_sample_id(style_name, idx)
                try:
                    sample = future.result()
                    if sample is None:
                        error_item = {"sample_id": sample_id, "style": style_name, "error": "生成失败"}
                        ef.write(json.dumps(error_item, ensure_ascii=False) + "\n")
                        ef.flush()
                        pbar.update(1)
                        continue

                    f.write(json.dumps(sample, ensure_ascii=False) + "\n")
                    f.flush()
                    success_count += 1
                    pbar.update(1)
                except Exception as exc:
                    error_item = {"sample_id": sample_id, "style": style_name, "error": str(exc)}
                    ef.write(json.dumps(error_item, ensure_ascii=False) + "\n")
                    ef.flush()
                    print(f"\n处理样本 {idx} 时出错: {exc}")
                    pbar.update(1)

    pbar.close()
    return success_count


def iter_jsonl(path: str) -> Iterable[Dict[str, Any]]:
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except Exception:
                continue


def merge_outputs(enabled_styles: List[str]) -> Tuple[str, str, Dict[str, Any]]:
    """合并各风格 jsonl，并生成 json/jsonl 两种格式。"""
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    merged_jsonl = os.path.join(config.OUTPUT_DIR, "train_data_v8.3.1.jsonl")
    merged_json = os.path.join(config.OUTPUT_DIR, "train_data_v8.3.1.json")
    report_json = os.path.join(config.OUTPUT_DIR, "quality_report_v8.3.1.json")

    rows: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for style in enabled_styles:
        file_path = os.path.join(config.OUTPUT_DIR, config.OUTPUT_FILE_PATTERN.format(style=style))
        for obj in iter_jsonl(file_path) or []:
            sample_id = str(obj.get("sample_id", ""))
            if sample_id and sample_id in seen:
                continue
            if sample_id:
                seen.add(sample_id)
            rows.append(obj)

    # 合并后打乱，避免训练时先全表格再全列表。
    rng = random.Random(config.RANDOM_SEED)
    rng.shuffle(rows)

    with open(merged_jsonl, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    with open(merged_json, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    report = build_quality_report(rows)
    with open(report_json, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return merged_jsonl, merged_json, report


def build_quality_report(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    style_counts: Dict[str, int] = {}
    qc_passed = 0
    issue_counter: Dict[str, int] = {}
    avg_input_len = 0.0
    avg_output_len = 0.0

    for row in rows:
        meta = row.get("meta", {}) if isinstance(row.get("meta"), dict) else {}
        style = meta.get("style", row.get("style", "Unknown"))
        style_counts[style] = style_counts.get(style, 0) + 1

        if meta.get("qc_passed"):
            qc_passed += 1
        for issue in meta.get("qc_issues", []) or []:
            key = str(issue).split(":")[0]
            issue_counter[key] = issue_counter.get(key, 0) + 1

        avg_input_len += len(str(row.get("input", "")))
        avg_output_len += len(str(row.get("output", "")))

    count = len(rows)
    if count:
        avg_input_len = round(avg_input_len / count, 2)
        avg_output_len = round(avg_output_len / count, 2)

    return {
        "count": count,
        "style_counts": style_counts,
        "qc_passed_count": qc_passed,
        "qc_passed_rate": round(qc_passed / count, 4) if count else None,
        "avg_input_len": avg_input_len,
        "avg_output_len": avg_output_len,
        "issue_counter": issue_counter,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SmartSummary-Pro v8.3.1 数据合成管线")
    parser.add_argument("--samples_per_style", type=int, default=config.SAMPLES_PER_STYLE)
    parser.add_argument("--styles", type=str, nargs="*", default=None, help="可选: from list")
    parser.add_argument("--no_resume", action="store_true", help="不使用断点续跑，直接追加生成")
    parser.add_argument("--no_strict_validation", action="store_true", help="质检失败也保留样本")
    parser.add_argument("--merge_only", action="store_true", help="不生成新样本，只合并现有输出")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    enabled_styles = args.styles if args.styles else get_enabled_styles()
    invalid_styles = [style for style in enabled_styles if style not in PROMPT_MAP]
    if invalid_styles:
        raise ValueError(f"Unsupported styles: {invalid_styles}")

    enabled_prompt_map = {style: PROMPT_MAP[style] for style in enabled_styles}

    print(
        f"开始数据合成任务 | 目标：{len(enabled_prompt_map)} 种风格 x "
        f"{args.samples_per_style} 条"
    )
    print(f"   启用风格：{', '.join(enabled_styles)}")
    print(f"   配置: 模型={config.MODEL_NAME}, 温度={config.TEMPERATURE}, Top-p={config.TOP_P}, 随机种子={config.RANDOM_SEED}")
    print(f"   并行度: {config.NUM_WORKERS} 个线程")
    print(f"   输出目录: {config.OUTPUT_DIR}")

    if not args.merge_only:
        for style_name, prompt_template in enabled_prompt_map.items():
            success_count = generate_style_samples(
                style_name=style_name,
                prompt_template=prompt_template,
                total_samples=args.samples_per_style,
                resume=not args.no_resume,
                strict_validation=not args.no_strict_validation,
            )
            print(f"{style_name} 风格新增完成: {success_count}/{args.samples_per_style} 条")

    merged_jsonl, merged_json, report = merge_outputs(enabled_styles)
    print("\n所有数据处理完毕！")
    print(f"合并 JSONL: {merged_jsonl}")
    print(f"合并 JSON : {merged_json}")
    print("质量报告:")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
