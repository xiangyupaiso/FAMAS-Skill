#!/usr/bin/env python3
"""
FAMAS v2.0 一致性校验器

用法（在仓库任意位置）：
    python tools/validate.py
    python tools/validate.py --strict   # 警告也视为失败

依赖：PyYAML（pip install pyyaml）；标准库 json / re / glob / pathlib。

覆盖 8 组检查：
  1 语法        所有 YAML / JSON 可解析
  2 引用        能力注册 → 契约块 / 语义字段 / 能力文件；provider coverage
  3 模板        模板占位符 → 契约字段；envelope 引用 → 契约/工作流 inputs
  4 编排        include 展开（含 synthesis 抑制）、环检测、判断层顺序、render 存在
  5 覆盖        能力所需语义字段的 provider 覆盖（assumption-driven 允许豁免）
  6 文档        markdown 相对链接、固定免责声明、版本号一致性
  7 合规闸      禁止词表能拦截越界样例且不误杀合规样例
  8 一致性补强  工作流版本、provider 声明自洽、规则锚点、输出闸语法、覆盖表统计

退出码：0 = 通过；1 = 有错误；2 = --strict 且有警告。
本脚本只做结构验证，不取任何行情数据、不产出任何数值结论。
"""
from __future__ import annotations

import ast
import glob
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)

try:
    import yaml
except ImportError:
    print("缺少依赖 PyYAML，请先执行: pip install pyyaml")
    sys.exit(2)

STRICT = "--strict" in sys.argv
errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def load(path: str):
    with open(path, encoding="utf-8") as f:
        return json.load(f) if path.endswith(".json") else yaml.safe_load(f)


def rel(path: str) -> str:
    return path.replace("\\", "/")


# ---------- 1 语法 ----------
yamls = sorted(glob.glob("**/*.yaml", recursive=True))
jsons = sorted(glob.glob("**/*.json", recursive=True))
parsed: dict[str, object] = {}
for p in yamls + jsons:
    try:
        parsed[rel(p)] = load(p)
    except Exception as e:  # noqa: BLE001
        err(f"[语法] {rel(p)}: {type(e).__name__}: {e}")

reg = parsed.get("core/capability-registry.yaml") or {}
sem = parsed.get("data/semantic-fields.yaml") or {}
contract = parsed.get("contracts/famas.contract.json") or {}
caps = reg.get("capabilities", []) if isinstance(reg, dict) else []
fields_def = sem.get("fields", {}) if isinstance(sem, dict) else {}
blocks = contract.get("blocks", {}) if isinstance(contract, dict) else {}
envelope_props = set((contract.get("envelope", {}) or {}).get("properties", {}))
cap_ids = {c["id"] for c in caps}
templates = {
    Path(p).stem for p in glob.glob("templates/*.md")
} - {"_render"}

DISCLAIMER = (
    "本报告仅作信息整理与适配度分析，不构成投资建议。"
    "基金过往业绩不预示未来表现。市场有风险，投资需谨慎。"
)

# ---------- 2 引用 ----------
produced = set()
for c in caps:
    for f in c.get("requires", []):
        if f not in fields_def:
            err(f"[引用] 能力 {c['id']} 引用了未定义语义字段 {f}")
    for o in c.get("outputs", []):
        produced.add(o)
        if o not in blocks:
            err(f"[引用] 能力 {c['id']} 的输出 {o} 没有契约块")
    if not Path(c.get("file", "")).exists():
        err(f"[引用] 能力 {c['id']} 的文件不存在: {c.get('file')}")
for b in blocks:
    if b not in produced and b not in {"alert", "decision_log"}:
        warn(f"[引用] 契约块 {b} 不由任何能力产出")

for p in sorted(glob.glob("data/providers/*.yaml")):
    d = parsed.get(rel(p)) or {}
    for f in d.get("coverage", []):
        if f not in fields_def:
            err(f"[引用] provider {rel(p)} 覆盖未定义字段 {f}")
    if "runtime-discovered" not in str(d.get("tool_names", "")):
        warn(f"[引用] provider {rel(p)} 的 tool_names 未声明运行时探测")

workflows: dict[str, dict] = {}
for p in sorted(glob.glob("workflows/**/*.yaml", recursive=True)):
    d = parsed.get(rel(p)) or {}
    wid = d.get("id")
    if not wid:
        err(f"[引用] {rel(p)} 缺少 id")
        continue
    workflows[wid] = d
    if not rel(p).endswith(wid + ".yaml"):
        err(f"[引用] 工作流 id 与路径不一致: {wid} vs {rel(p)}")

all_inputs = {k for d in workflows.values() for k in (d.get("inputs") or {})}

# ---------- 3 模板占位符 ----------
loopvars = {"f", "h", "r", "a", "x", "s", "i", "level"}
envelope_allowed = envelope_props | all_inputs | {"inputs", "alerts"}
for p in sorted(glob.glob("templates/*.md")):
    if p.endswith("_render.md"):
        continue
    txt = Path(p).read_text(encoding="utf-8")
    for raw in re.findall(r"\{\{\s*([^}]+?)\s*\}\}", txt):
        expr = raw.split("|")[0].strip()
        if expr == "fixed_disclaimer":
            continue
        target = expr
        if expr.startswith("provenance("):
            target = expr[len("provenance("):].rstrip(")")
        m = re.search(r"([A-Za-z_][A-Za-z_0-9]*)\.([A-Za-z_][A-Za-z_0-9]*)", target)
        if not m:
            continue
        b, f = m.group(1), m.group(2)
        if b in loopvars:
            continue
        if b == "envelope":
            if f not in envelope_allowed:
                err(f"[模板] {rel(p)}: envelope.{f} 未在契约或工作流 inputs 中定义")
            continue
        if b not in blocks:
            err(f"[模板] {rel(p)}: 未知契约块 {b} (表达式 {expr})")
            continue
        if f not in blocks[b].get("fields", []):
            err(f"[模板] {rel(p)}: {b}.{f} 不在契约字段清单")

# ---------- 4 编排 ----------
def collect_uses(node) -> list[str]:
    out: list[str] = []
    if isinstance(node, dict):
        if "use" in node:
            out.append(node["use"])
        if "parallel" in node:
            out.extend(node["parallel"])
        for key in ("loop", "conditional"):
            if key in node and isinstance(node[key], dict) and "use" in node[key]:
                out.append(node[key]["use"])
        if "branch" in node and isinstance(node["branch"], dict):
            for case in node["branch"].get("cases", []):
                out.extend(collect_uses(case))
            if node["branch"].get("default") not in (None, "noop"):
                out.append(node["branch"]["default"])
        handled = {"use", "parallel", "loop", "conditional", "branch"}
        for k, v in node.items():
            if k in handled:
                continue
            if isinstance(v, (dict, list)):
                out.extend(collect_uses(v))
    elif isinstance(node, list):
        for v in node:
            out.extend(collect_uses(v))
    return out


def includes(node):
    if isinstance(node, dict):
        if "include" in node:
            yield node["include"]["workflow"]
        for v in node.values():
            yield from includes(v)
    elif isinstance(node, list):
        for v in node:
            yield from includes(v)


def expand(wid: str, stack: tuple[str, ...]) -> list[dict]:
    if wid in stack:
        err(f"[编排] include 成环: {' -> '.join(stack + (wid,))}")
        return []
    d = workflows.get(wid)
    if d is None:
        err(f"[编排] include 目标不存在: {wid}")
        return []
    seq: list[dict] = []
    for s in d.get("steps", []):
        if not isinstance(s, dict):
            continue
        for target in includes(s):
            if target not in workflows:
                err(f"[编排] {wid} include 目标不存在: {target}")
            else:
                seq.extend(expand(target, stack + (wid,)))
        if "include" not in s:
            seq.append(s)
    # 被 include 的子工作流：抑制 synthesis，只保留事实/判断层步骤
    if stack:
        seq = [s for s in seq if s.get("use") != "synthesis"]
    return seq


for wid, d in workflows.items():
    for t in includes(d.get("steps", [])):
        if t not in workflows:
            err(f"[编排] {wid} include 目标不存在: {t}")
    if d.get("render") not in templates:
        err(f"[编排] {wid} 的 render 模板不存在: {d.get('render')}")
    uses = [u for u in collect_uses(d.get("steps", [])) if u != "noop"]
    for u in uses:
        if u not in cap_ids:
            err(f"[编排] {wid} 引用未登记能力: {u}")
    if "synthesis" in uses and uses[-1] != "synthesis":
        err(f"[编排] {wid} 的 synthesis 不是最后一个业务步骤")
    if "devils_advocate" in uses and "synthesis" in uses:
        if uses.index("devils_advocate") > uses.index("synthesis"):
            err(f"[编排] {wid} 的 devils_advocate 排在 synthesis 之后")
    expanded = expand(wid, ())
    exp_uses = [u for u in collect_uses(expanded) if u != "noop"]
    n_syn = exp_uses.count("synthesis")
    if n_syn > 1:
        err(f"[编排] {wid} 展开后含 {n_syn} 个 synthesis（include 抑制规则失效）")
    if n_syn == 1 and exp_uses[-1] != "synthesis":
        err(f"[编排] {wid} 展开后 synthesis 不是最后一步")

# ---------- 5 字段覆盖 ----------
covered: set[str] = set()
for p in glob.glob("data/providers/*.yaml"):
    covered |= set((parsed.get(rel(p)) or {}).get("coverage", []))
needed = {f for c in caps for f in c.get("requires", [])}
assumption_driven = {
    f for f, meta in fields_def.items()
    if isinstance(meta, dict) and meta.get("source_type") == "assumption-driven"
}
for f in sorted(needed - covered - assumption_driven):
    err(f"[覆盖] 语义字段 {f} 无任何 provider 声明覆盖，且未标 assumption-driven")
for f in sorted(assumption_driven):
    if "assumptions" not in Path("capabilities/cost_model.md").read_text(encoding="utf-8"):
        err(f"[覆盖] 假设驱动字段 {f} 缺少能力侧的 assumptions 处理说明")

# ---------- 6 文档 ----------
for doc in ["README.md", "MIGRATION.md", "SETUP.md", "core/SKILL.md",
            "workflows/_schema.md", "judgment/README.md"]:
    txt = Path(doc).read_text(encoding="utf-8")
    for link in re.findall(r"\[[^\]]*\]\(([^)#]+\.(?:md|json|yaml|txt))\)", txt):
        target = Path(os.path.normpath(os.path.join(os.path.dirname(doc), link)))
        if not target.exists() and not Path(link).exists():
            err(f"[文档] {doc} 断链 -> {link}")
for doc in ["policies/compliance.md", "README.md", "AGENTS.md", "core/SKILL.md"]:
    if DISCLAIMER not in Path(doc).read_text(encoding="utf-8"):
        err(f"[文档] {doc} 的固定免责声明未逐字一致")
versions = {
    "core/SKILL.md": 'version: "2.0.0"',
    "contracts/famas.contract.json": '"version": "2.0.0"',
    "core/capability-registry.yaml": 'version: "2.0.0"',
    "data/semantic-fields.yaml": 'version: "2.0.0"',
    "triggers/rules.yaml": 'version: "2.0.0"',
    "judgment/lenses.yaml": 'version: "2.0.0"',
    "judgment/veto-rules.yaml": 'version: "2.0.0"',
}
for p, needle in versions.items():
    if needle not in Path(p).read_text(encoding="utf-8"):
        err(f"[文档] {p} 版本号未同步到 2.0.0")

# ---------- 7 合规闸 ----------
words = [
    l.strip() for l in Path("policies/forbidden-words.txt").read_text(encoding="utf-8").splitlines()
    if l.strip() and not l.strip().startswith("#")
]
violating = "综合来看该基金值得入手，建议加仓，优先关注，目标价 XX，稳赚无风险收益。"
compliant = "该基金对稳健型投资者的适配度为中等，需关注规模变化与经理任职状态。"
hits_bad = [w for w in words if w in violating]
hits_good = [w for w in words if w in compliant]
if not hits_bad:
    err("[合规闸] 越界样例未被拦截（禁止词表漏检）")
if hits_good:
    err(f"[合规闸] 合规样例被误杀: {hits_good}")
if len(words) < 20:
    err("[合规闸] 禁止词表条目过少，疑似文件解析错误")

# ---------- 8 一致性补强（2026-11-07 真实 MCP 首跑 / 补测） ----------
core_ver = re.search(r'version:\s*"([0-9.]+)"', Path("core/SKILL.md").read_text(encoding="utf-8"))
if core_ver:
    for wid, d in workflows.items():
        if str(d.get("version", "")) != core_ver.group(1):
            err(f"[一致性] 工作流 {wid} 版本 {d.get('version')} 与 core/SKILL.md {core_ver.group(1)} 不一致")
else:
    err("[一致性] core/SKILL.md 未声明 version")

for p in sorted(glob.glob("data/providers/*.yaml")):
    d = parsed.get(rel(p)) or {}
    if not isinstance(d, dict):
        continue
    overlap = set(d.get("coverage", [])) & set(d.get("known_gaps", []))
    if overlap:
        err(f"[一致性] provider {rel(p)} 的 coverage 与 known_gaps 冲突: {sorted(overlap)}")
    for k, v in (d.get("trust_by_source_type") or {}).items():
        if v not in {"L1", "L2", "L3", "L4"}:
            err(f"[一致性] provider {rel(p)} 的 trust_by_source_type.{k} 非法等级 {v}")
    for f in d.get("known_gaps", []):
        if f not in fields_def:
            err(f"[一致性] provider {rel(p)} 的 known_gaps 含未定义字段 {f}")

rule_anchors = {
    "judgment/veto-rules.yaml": ["cross_document_recall", "benchmark_version_change"],
    "capabilities/periodic_report_reader.md": ["document_title_match", "rejected_cross_document"],
    "capabilities/devils_advocate.md": ["⑥ 来源身份反证"],
    "capabilities/performance_metrics.md": ["基准版本核对"],
    "data/gateway.md": ["implausible_value", "指标级权限差异", "文档身份误召回"],
    "data/semantic-fields.yaml": ["versioning", "retrieval_granularity"],
    "policies/source-trust.md": ["文档身份校验", "指标级无权限"],
    "templates/periodic_report_memo.md": ["not_retrievable_sections"],
    "workflows/data-quality/cross_source_verify.yaml": ["单源降级"],
}
for p, needles in rule_anchors.items():
    txt = Path(p).read_text(encoding="utf-8")
    for n in needles:
        if n not in txt:
            err(f"[一致性] {p} 缺少规则锚点 {n}")

gate = Path("tools/check_report.py")
if not gate.exists():
    err("[一致性] 缺少输出闸 tools/check_report.py")
else:
    try:
        ast.parse(gate.read_text(encoding="utf-8"))
    except SyntaxError as e:
        err(f"[一致性] 输出闸语法错误: {e}")

probe = Path("runs/2026-11-07/field_probe.md")
if probe.exists():
    ptxt = probe.read_text(encoding="utf-8")
    rows = re.findall(
        r"^\|\s*`([a-z_]+)`\s*\|\s*\*{0,2}(OK|PARTIAL|MISS|N/A)\*{0,2}\s*\|",
        ptxt, re.M,
    )
    counts = Counter(s for _, s in rows)
    actual = (counts["OK"], counts["PARTIAL"], counts["MISS"], counts["N/A"])
    m = re.search(r"\*\*统计\*\*：OK (\d+) · PARTIAL (\d+) · MISS (\d+) · N/A (\d+)", ptxt)
    if not m:
        warn("[一致性] field_probe.md 缺少可解析的覆盖统计行")
    else:
        declared = tuple(int(x) for x in m.groups())
        if declared != actual:
            err(f"[一致性] 覆盖表统计不一致：声明 {declared}，实际 {actual}")
        if sum(actual) != len(fields_def):
            err(f"[一致性] 覆盖表字段数 {sum(actual)} != 语义字段字典 {len(fields_def)}")

# ---------- 汇总 ----------
print(f"FAMAS v2.0 校验 | 文件 {len([p for p in glob.glob('**/*', recursive=True) if os.path.isfile(p)])} "
      f"| YAML {len(yamls)} | JSON {len(jsons)} | 工作流 {len(workflows)} "
      f"| 能力 {len(cap_ids)} | 语义字段 {len(fields_def)} | 契约块 {len(blocks)} "
      f"| 模板 {len(templates)} | provider {len(glob.glob('data/providers/*.yaml'))}")
print(f"8 组检查完成 | 错误 {len(errors)} | 警告 {len(warnings)} | "
      f"禁止词 {len(words)} 条（越界样例命中 {len(hits_bad)}）")
for e in errors:
    print("  ERROR  ", e)
for w in warnings:
    print("  WARN   ", w)
if errors:
    print("结论：未通过")
    sys.exit(1)
if STRICT and warnings:
    print("结论：--strict 模式下警告视为失败")
    sys.exit(2)
print("结论：通过")
sys.exit(0)
