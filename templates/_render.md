# 模板渲染规则

> 模板**只负责渲染**，不定义字段、不写计算口径、不写合规条款。所有占位符必须对应 `contracts/famas.contract.json` 中的字段。

## 语法

- `{{ block.field }}` — 契约字段
- `{{ envelope.* }}` — 信封字段（workflow_id、generated_at、missing_fields…）
- `{{ provenance(block.field) }}` — 渲染为 "来源：X · 时点：Y · 等级：Z"
- `{% if %}` / `{% for %}` — 仅条件与循环，不做运算
- `{{ fixed_disclaimer }}` — 固定免责声明，**逐字取自 `policies/compliance.md` 第四节**

## 强制段落（所有模板）

```
1. 数据说明（来源、时点、等级口径）
2. 核心风险提示（必须在综合结论之前）
3. 正文
4. 数据缺口与来源分歧（即使为空也要写"无"或显式列出）
5. 固定免责声明（逐字、末尾）
```

## 规则

| # | 规则 |
|---|---|
| R1 | 任何数值占位符渲染时必须同时输出 `provenance()`；缺 provenance 则渲染为「数据未覆盖」 |
| R2 | `estimated: true` 的字段渲染时追加「（估算）」 |
| R3 | `second_hand: true` 追加「非一手来源，需核实原文」 |
| R4 | `missing_fields` 非空时，在正文对应位置标「该维度数据未覆盖」，不得留白 |
| R5 | `source_conflicts` 非空时，渲染成「来源分歧」表，列全部来源与取值 |
| R6 | 模板不得包含评价性措辞、交易信号、推荐语 |
| R7 | 渲染完成后由 Core 执行 `policies/compliance.md` 输出前检查清单 |

## 模板索引

| 模板 | 用途 | 主要消费方 |
|---|---|---|
| `rating_card.md` | 综合评级卡 | `core/a_single_fund`、`events/alert_reassessment` |
| `screening_report.md` | 筛选 / 对比报告 | `core/b_screen`、`research/*` |
| `portfolio_diagnosis.md` | 组合诊断报告 | `core/c_portfolio`、`lifecycle/*` |
| `alert_report.md` | 监控预警报告 | `core/d_monitor` |
| `decision_memo.md` | 四段式决策备忘（四段式框架） | `events/*`、`lifecycle/fund_replacement`、判断层场景 |
| `periodic_report_memo.md` | 定期报告阅读备忘（季报/半年报/年报） | `events/periodic_report_deep_read`、`research/report_consistency_check` |
| `calibration_report.md` | 决策日志季度校准报告 | `judgment/quarterly_calibration` |
