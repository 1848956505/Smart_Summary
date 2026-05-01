#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_train_data_v8_3_2.py

用于修复 train_data_v8.3.2.jsonl 中的轻量格式与文本问题：
1. 清理 output 末尾残留的单独右花括号 "}"；
2. 将表格风格样本的 meta.style_key 从 "from" 修正为 "table"；
3. 清理 output 中残留的口语脏词/情绪词；
4. 标记可能存在“数字推断扩写”风险的样本；
5. 输出修复后的 JSONL 与修复报告 JSON。

默认不删除样本，只做保守修复。
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple


VULGAR_REPLACEMENTS: Dict[str, str] = {
    # 脏词：直接去掉，不改变事实含义
    "妈的": "",
    "特么": "",
    "尼玛": "",
    "我靠": "",

    # 情绪词：弱化为正式表达，避免训练模型学会口语化情绪输出
    "烦死了": "较为困扰",
    "累死": "较为耗时",
    "唉": "",
    "哎": "",
}

FORBIDDEN_CLOSINGS = [
    "以上为本周工作总结",
    "以上就是本周工作总结",
    "如需进一步优化",
    "如需我继续",
    "希望对你有帮助",
    "希望对您有帮助",
]


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            raw = line.strip()
            if not raw:
                continue
            try:
                rows.append(json.loads(raw))
            except json.JSONDecodeError as exc:
                raise ValueError(f"JSONL 解析失败：line={line_no}, error={exc}") from exc
    return rows


def dump_jsonl(rows: List[Dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def fix_trailing_brace(output: str) -> Tuple[str, bool]:
    """
    修复 output 末尾孤立的右花括号。
    只处理末尾单独残留，不处理中间正文，避免误伤正常内容。
    """
    fixed = output.rstrip()
    if fixed.endswith("}"):
        fixed = fixed[:-1].rstrip()
        return fixed, True
    return output, False


def fix_style_key(row: Dict[str, Any]) -> bool:
    """
    将表格风格样本的 style_key 从 from 修正为 table。
    """
    meta = row.get("meta")
    if not isinstance(meta, dict):
        return False

    style = meta.get("style")
    style_key = meta.get("style_key")
    instruction = row.get("instruction", "")

    is_table_style = style == "表格风格" or "表格风格" in instruction
    if is_table_style and style_key == "from":
        meta["style_key"] = "table"
        return True
    return False


def sanitize_vulgar_words(output: str) -> Tuple[str, List[str]]:
    """
    清理 output 中残留的脏词/强情绪词。
    """
    fixed = output
    hits: List[str] = []
    for word, replacement in VULGAR_REPLACEMENTS.items():
        if word in fixed:
            hits.append(word)
            fixed = fixed.replace(word, replacement)

    # 清理替换后可能出现的引号内多余空白
    fixed = re.sub(r"“\s+", "“", fixed)
    fixed = re.sub(r"\s+”", "”", fixed)
    fixed = re.sub(r"[ \t]{2,}", " ", fixed)
    fixed = re.sub(r"\n{3,}", "\n\n", fixed)
    return fixed.strip(), hits


def remove_forbidden_closings(output: str) -> Tuple[str, List[str]]:
    """
    保守移除禁用包装/结语句。
    """
    fixed = output
    removed: List[str] = []
    for phrase in FORBIDDEN_CLOSINGS:
        if phrase in fixed:
            removed.append(phrase)
            fixed = fixed.replace(phrase, "")
    fixed = re.sub(r"\n{3,}", "\n\n", fixed).strip()
    return fixed, removed


def detect_numeric_inference_risk(row: Dict[str, Any]) -> List[str]:
    """
    标记可能存在“数字推断扩写”的样本。
    只做风险提示，不自动改写，避免误伤正确样本。

    典型风险：
    input: 发现3个BUG，其中1个还没确认
    output: 2个已提交，1个待确认
    """
    text_in = row.get("input", "")
    text_out = row.get("output", "")
    risks: List[str] = []

    has_total_and_uncertain = bool(
        re.search(r"([2-9]|[二三四五六七八九十])\s*个", text_in)
        and re.search(r"(一个|1个|一项|1项).{0,12}(没确认|未确认|待确认|不确定|还没定|尚未确认)", text_in)
    )
    has_split_number_in_output = bool(
        re.search(r"(其中)?\s*([1-9]|[一二三四五六七八九十])\s*个.{0,12}(已|完成|提交|确认)", text_out)
        and re.search(r"([1-9]|[一二三四五六七八九十])\s*个.{0,12}(待确认|未确认|不确定)", text_out)
    )

    if has_total_and_uncertain and has_split_number_in_output:
        risks.append("可能将总数与待确认项拆分成未提供的新数值")

    return risks


def validate_rows(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    style_counter = Counter()
    style_key_counter = Counter()
    bad_word_counter = Counter()
    trailing_brace_ids: List[str] = []
    missing_field_ids: List[str] = []
    table_style_without_table: List[str] = []
    list_style_with_table: List[str] = []

    required_fields = {"sample_id", "instruction", "input", "output", "meta"}

    for row in rows:
        sid = row.get("sample_id", "<unknown>")
        missing = required_fields - set(row.keys())
        if missing:
            missing_field_ids.append(sid)

        output = row.get("output", "")
        meta = row.get("meta", {})
        style = meta.get("style") if isinstance(meta, dict) else None
        style_key = meta.get("style_key") if isinstance(meta, dict) else None

        style_counter[style] += 1
        style_key_counter[style_key] += 1

        if output.rstrip().endswith("}"):
            trailing_brace_ids.append(sid)

        for word in VULGAR_REPLACEMENTS:
            if word in output:
                bad_word_counter[word] += 1

        if style == "表格风格" and "|" not in output:
            table_style_without_table.append(sid)
        if style == "列表风格" and re.search(r"\n\|.+\|\n\|", output):
            list_style_with_table.append(sid)

    return {
        "count": len(rows),
        "style_counts": dict(style_counter),
        "style_key_counts": dict(style_key_counter),
        "remaining_trailing_brace_count": len(trailing_brace_ids),
        "remaining_trailing_brace_ids": trailing_brace_ids[:50],
        "remaining_vulgar_word_counter": dict(bad_word_counter),
        "missing_field_count": len(missing_field_ids),
        "missing_field_ids": missing_field_ids[:50],
        "table_style_without_table_count": len(table_style_without_table),
        "table_style_without_table_ids": table_style_without_table[:50],
        "list_style_with_table_count": len(list_style_with_table),
        "list_style_with_table_ids": list_style_with_table[:50],
    }


def repair_dataset(input_path: Path, output_path: Path, report_path: Path) -> Dict[str, Any]:
    rows = load_jsonl(input_path)

    repair_counter = Counter()
    repaired_ids = defaultdict(list)
    numeric_risk_ids: List[Dict[str, Any]] = []

    for row in rows:
        sid = row.get("sample_id", "<unknown>")

        # 1. 修复 style_key
        if fix_style_key(row):
            repair_counter["fixed_style_key_from_to_table"] += 1
            repaired_ids["fixed_style_key_from_to_table"].append(sid)

        # 2. 修复 output 文本
        output = row.get("output", "")
        if not isinstance(output, str):
            output = str(output)

        output, fixed_brace = fix_trailing_brace(output)
        if fixed_brace:
            repair_counter["removed_trailing_brace"] += 1
            repaired_ids["removed_trailing_brace"].append(sid)

        output, vulgar_hits = sanitize_vulgar_words(output)
        if vulgar_hits:
            repair_counter["sanitized_vulgar_or_emotional_words"] += 1
            repaired_ids["sanitized_vulgar_or_emotional_words"].append(sid)
            for word in vulgar_hits:
                repair_counter[f"sanitized_word::{word}"] += 1

        output, removed_closings = remove_forbidden_closings(output)
        if removed_closings:
            repair_counter["removed_forbidden_closings"] += 1
            repaired_ids["removed_forbidden_closings"].append(sid)
            for phrase in removed_closings:
                repair_counter[f"removed_closing::{phrase}"] += 1

        row["output"] = output

        # 3. 记录修复动作到 meta.cleaning_actions
        meta = row.get("meta")
        if isinstance(meta, dict):
            actions = meta.get("cleaning_actions")
            if not isinstance(actions, list):
                actions = []
            if fixed_brace:
                actions.append("removed_trailing_brace")
            if vulgar_hits:
                actions.append("sanitized_vulgar_or_emotional_words")
            if removed_closings:
                actions.append("removed_forbidden_closings")
            if actions:
                # 去重但保序
                meta["cleaning_actions"] = list(dict.fromkeys(actions))

        # 4. 数字推断风险只标记，不自动修
        risks = detect_numeric_inference_risk(row)
        if risks:
            numeric_risk_ids.append({
                "sample_id": sid,
                "risks": risks,
            })

    dump_jsonl(rows, output_path)

    report = {
        "input_file": str(input_path),
        "output_file": str(output_path),
        "total_rows": len(rows),
        "repair_counter": dict(repair_counter),
        "repaired_ids": {k: v[:100] for k, v in repaired_ids.items()},
        "numeric_inference_risk_count": len(numeric_risk_ids),
        "numeric_inference_risk_samples": numeric_risk_ids[:100],
        "validation_after_repair": validate_rows(rows),
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="修复工作总结正式数据集 v8.3.2 的轻量格式与文本问题。"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="输入 JSONL 文件路径，例如 train_data_v8.3.2.jsonl",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="输出修复后 JSONL 文件路径，例如 train_data_v8.3.2.fixed.jsonl",
    )
    parser.add_argument(
        "--report",
        required=True,
        help="输出修复报告 JSON 文件路径，例如 fix_report_v8.3.2.json",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    report = repair_dataset(
        input_path=Path(args.input),
        output_path=Path(args.output),
        report_path=Path(args.report),
    )

    print("修复完成。")
    print(f"输入文件：{report['input_file']}")
    print(f"输出文件：{report['output_file']}")
    print(f"总样本数：{report['total_rows']}")
    print("修复统计：")
    for key, value in report["repair_counter"].items():
        print(f"  - {key}: {value}")
    print(f"数字推断风险样本数：{report['numeric_inference_risk_count']}")
    print("修复后校验：")
    validation = report["validation_after_repair"]
    print(f"  - remaining_trailing_brace_count: {validation['remaining_trailing_brace_count']}")
    print(f"  - remaining_vulgar_word_counter: {validation['remaining_vulgar_word_counter']}")
    print(f"  - style_key_counts: {validation['style_key_counts']}")


if __name__ == "__main__":
    main()
