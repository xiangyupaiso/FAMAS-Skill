#!/usr/bin/env python3
"""
FAMAS 输出闸 — 对运行产物做「合规 + 口径 + 溯源」扫描

用法（在仓库任意位置）：
    python tools/check_report.py                     # 扫描 runs/ 下全部 .md/.html
    python tools/check_report.py --path PATH        # 指定文件或目录
    python tools/check_report.py --strict           # 警告也视为失败

与 tools/validate.py 的分工：
    validate.py   = 结构验证（仓库自身的 YAML/JSON/引用/编排）
    check_report  = 输出验证（实际交付给用户的报告能不能放行）

设计要点：
  * 禁止词扫描针对「交易指令语义」，不是词面。合规自检段落里引用 C1/C3 等编号、
    或用 <!-- compliance-meta:start/end --> 包裹的元描述，属于描述规则而非输出建议，
    因此豁免（这是 2026-11-07 首跑发现的自误伤根因）。
  * 口径规则来自 data/gateway.md 第四节与 decision 层规则，逐条落成可执行检查。
  * 不取任何行情数据、不联网、不修改被扫描文件。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DISCLAIMER = (
    "本报告仅作信息整理与适配度分析，不构成投资建议。"
    "基金过往业绩不预示未来表现。市场有风险，投资需谨慎。"
)

META_BLOCK = re.compile(
    r"<!--\s*compliance-meta:start\s*-->.*?<!--\s*compliance-meta:end\s*-->",
    re.S | re.I,
)
META_LINE = re.compile(r"^\s*(?:[-*>]|\d+[.)])?\s*C\d\b", re.M)

DOC_IDENTITY_MARKERS = (
    "document_title_match", "rejected_cross_document", "not_retrievable",
    "cross_document_recall",
)
BENCHMARK_MARKERS = (
    "生效日", "版本核对", "benchmark_version", "基准变更", "未核对", "versioning",
)


def forbidden_words() -> list[str]:
    p = ROOT / "policies" / "forbidden-words.txt"
    return [
        line.strip() for line in p.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def strip_meta(text: str) -> str:
    """移除合规元描述，只对真正的输出正文做字面扫描。"""
    text = META_BLOCK.sub("", text)
    return "\n".join(
        line for line in text.splitlines()
        if not META_LINE.match(line)
    )


def scan(path: Path, words: list[str]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    raw = path.read_text(encoding="utf-8")
    body = strip_meta(raw)
    name = path.name

    # 1 禁止词（正文）
    hits = [w for w in words if w in body]
    if hits:
        errors.append(f"禁止词命中（交易指令语义）: {hits}")

    # 2 固定免责声明逐字一致
    if DISCLAIMER not in raw:
        errors.append("固定免责声明缺失或与 policies/compliance.md 不逐字一致")

    # 以下只针对报告类产物（探测记录、模板说明等不强制）
    is_report = bool(re.search(r"业绩|净值|持仓|基金", raw)) and bool(
        re.search(r"来源|provenance|数据源", raw)
    )
    if not is_report:
        warnings.append("非报告类产物，跳过口径/溯源检查")
        return errors, warnings

    # 3 溯源与时间口径
    if not re.search(r"L1|L2|L3|置信度", raw):
        errors.append("缺少来源可信度等级标注（L1/L2/L3 或置信度）")
    if not re.search(r"2026-|2025-|YYYYQ|报告期|时点|截止", raw):
        errors.append("缺少数据时点/报告期标注，无法判断是否把历史数据写成当前")

    # 4 数据缺口与来源分歧必须显式列出（C7 / source-trust 第三节）
    if not re.search(r"missing_fields|数据缺口|未取到|未覆盖", raw):
        errors.append("未列出数据缺口（missing_fields）")
    if not re.search(r"source_conflicts|来源分歧|口径分歧|冲突", raw):
        warnings.append("未列出来源分歧段落；若无分歧应显式写「无分歧」")

    # 5 文档身份校验（跨文档误召回是 invalid 级风险）
    if re.search(r"§4\.4|报告期内基金投资策略和运作分析|原文摘录|quoted_excerpts|章节", raw):
        if not any(m in raw for m in DOC_IDENTITY_MARKERS):
            errors.append(
                "引用了定期报告章节，却未出现文档身份校验标记 "
                "(document_title_match / rejected_cross_document / not_retrievable)"
            )

    # 6 基准版本核对（报告期内基准变更会使跨期对照失效）
    if "业绩比较基准" in raw or "复合基准" in raw:
        if not any(m in raw for m in BENCHMARK_MARKERS):
            errors.append(
                "使用了业绩比较基准，却未核对生效日/版本（或明确标注未核对并列为待办）"
            )

    # 7 估算值不得伪装成实测
    if "estimated" in raw.lower() and not re.search(r"估算|假设驱动|assumption", raw, re.I):
        errors.append("出现 estimated 标记但未说明其为估算/假设驱动，存在伪装成实测的风险")

    # 8 结论强度与星级的一致性
    if re.search(r"confidence_cap\s*=\s*weak|结论强度为 `?weak|本轮结论强度", raw):
        if re.search(r"星级\s*[:：]\s*[1-5]|适配度\s*[:：]\s*(高|中|低)", raw):
            errors.append("结论强度 weak 却仍输出星级或适配度分档")

    return errors, warnings


def self_test(words: list[str]) -> list[str]:
    """检查器自身自检：越界能拦、合规不误杀、元描述不误杀。"""
    problems: list[str] = []
    violating = "综合来看该基金值得入手，建议加仓，优先关注，目标价 1.25，稳赚无风险收益。"
    compliant = "该基金对稳健型投资者的适配度为中等，需关注规模变化与经理任职状态。"
    meta = (
        "<!-- compliance-meta:start -->\n"
        "- C1 禁止词扫描 0 命中\n"
        "- C3 无推荐措辞，全文为适配度表述\n"
        "<!-- compliance-meta:end -->\n"
    )
    if not [w for w in words if w in strip_meta(violating)]:
        problems.append("自检失败：越界样例未被拦截")
    if [w for w in words if w in strip_meta(compliant)]:
        problems.append("自检失败：合规样例被误杀")
    if [w for w in words if w in strip_meta(meta)]:
        problems.append("自检失败：合规元描述被字面匹配误杀（豁免逻辑失效）")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description="FAMAS 输出闸")
    ap.add_argument("--path", default="runs", help="要扫描的文件或目录，默认 runs/")
    ap.add_argument("--strict", action="store_true", help="警告也视为失败")
    args = ap.parse_args()

    target = Path(args.path)
    if not target.is_absolute():
        target = ROOT / target
    files = (
        sorted([p for p in target.rglob("*") if p.suffix.lower() in {".md", ".html"}])
        if target.is_dir() else [target]
    )
    if not files:
        print(f"没有找到可扫描文件: {target}")
        return 2

    words = forbidden_words()
    all_errors: list[str] = []
    all_warnings: list[str] = []
    for p in files:
        errs, warns = scan(p, words)
        for e in errs:
            all_errors.append(f"{p.relative_to(ROOT) if p.is_relative_to(ROOT) else p.name}: {e}")
        for w in warns:
            all_warnings.append(f"{p.relative_to(ROOT) if p.is_relative_to(ROOT) else p.name}: {w}")
        status = "FAIL" if errs else ("WARN" if warns else "PASS")
        print(f"  [{status:4}] {p.name}")

    all_errors.extend(f"SELF-TEST: {m}" for m in self_test(words))

    print(f"\n输出闸 | 文件 {len(files)} | 禁止词 {len(words)} 条 | "
          f"错误 {len(all_errors)} | 警告 {len(all_warnings)}")
    for e in all_errors:
        print("  ERROR  ", e)
    for w in all_warnings:
        print("  WARN   ", w)
    if all_errors:
        print("结论：未通过，报告不得交付")
        return 1
    if args.strict and all_warnings:
        print("结论：--strict 模式下警告视为失败")
        return 2
    print("结论：通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
