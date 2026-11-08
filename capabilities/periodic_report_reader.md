# periodic_report_reader — 定期报告阅读（事实层）

> `layer: fact` · 无 persona · 把「季报 / 中期报告（半年报） / 年度报告」当作**被阅读的文档**，而不只是持仓数据的来源标签
> 输出块见 `contracts/famas.contract.json#/blocks/periodic_report`

## 定位

v2.0 只把定期报告当作 `holdings` 的来源，缺了「读报告」这一环。本能力补齐：基金评估必须能系统阅读并复述披露文档，且**只做事实提取与原文摘录，不评价管理人、不预测**。

## 输入

`fund_code` · `report_type`（`quarterly` / `interim` / `annual`）· `report_period`（YYYYQn 或 YYYYH1 / YYYY）· 可选 `compare_periods`

## 语义字段

`periodic_report_full` `manager_commentary` `portfolio_report` `financial_statements` `auditor_opinion` `report_holder_changes` `material_events` `report_fee_detail` `prospectus_terms` `narrative_history` `fund_announcements`

## 按报告类型的阅读清单

| 报告类型 | 必读章节 | 特别要求 |
|---|---|---|
| `quarterly` 季度报告 | 主要财务指标与净值表现、投资组合报告、管理人报告简述、份额变动 | 披露较简，**不得推定存在财务报表或审计意见**；缺章节标 `not_disclosed` |
| `interim` 中期报告（半年报） | 上述 + 财务报表与附注、持有人结构、重大事项 | 明确标注财务报表**是否未经审计** |
| `annual` 年度报告 | 全部上述 + 经审计财务报表、审计意见、完整管理人报告、治理与关联交易 | 审计意见类型**照录原文**，不得改写为"无问题" |

## 文档身份硬校验（2026-11-07 补测新增，最高优先级）

章节片段**能检索到，但跨文档误召回风险极高**：实测以「4.4.1 报告期内基金投资策略和运作分析」检索时，返回的前 4 条均为**其他基金**的同期章节（含"总仓位 90% 左右、港股约 36%、A 类净值增长 26.24%"），只有第 5 条是目标基金的 §3.2。若不校验标题，会把别的产品数据写入本基金事实块，产生方向性错误结论。

任何文档片段进入事实块前，逐条执行：

```
1 `document_title_match`：校验 title 含目标基金全称或简称；纯代码型片段需有其他字段能唯一定位主体
2 校验报告类型（季度/中期/年度）与报告期（YYYYQn / YYYYH1 / YYYY）与 inputs 一致
3 校验披露日期与 release_date 一致；同一标题多版本时取最新且标注版本
4 任一不匹配 -> 标 rejected_cross_document，整条丢弃，写入 not_retrievable_sections 的伴随说明
5 禁止用同管理人、同主题、名称相近基金（如"XX蓝筹精选"）的章节替代
```

命中 `judgment/veto-rules.yaml#cross_document_recall` 且未剔除 → 结论判 `invalid`。

## 阅读口径

1. **章节定位**：每个结论都能指回报告章节名与页码/段落，输出 `quoted_excerpts`
2. **原文优先**：管理人表述、审计意见、重大事项一律原文摘录，不做评价性改写
3. **三类对照**（只报差异，不下结论）：
   - **说的 vs 做的**：`manager_commentary` 与 `portfolio_report` / `holdings` 对照
   - **上期说的 vs 本期做的**：`narrative_history` 与本期实际对照
   - **合同 vs 实际**：`prospectus_terms` 与本期投资组合对照（股票仓位上下限、港股通权限、衍生品权限、业绩基准）
4. **费用交叉验证**：`report_fee_detail` 与 `fee_schedule` 口径差异，写入 `clause_consistency_findings`
5. **滞后性**：全部标注"报告期末快照，非实时"；报告期与披露日期并列

## 输出要求

- 结构化输出 `periodic_report` 块；每项带 `source`、`as_of`、`confidence`、`release_date`、章节定位
- 每个 `quoted_excerpts` 条目含 `section`、`text`、`page_or_para`
- 未披露章节标 `status: "not_disclosed"`，**不得留空、不得推测**
- **目标文档章节未命中时标 `status: "not_retrievable"` 并写入 `not_retrievable_sections`**：章节内容本身可能可检索，但目标基金/目标报告期的该章节未返回，属于检索排序与覆盖边界，不是披露义务边界。二者必须分开记录，禁止把 `not_retrievable` 写成"未披露"，也禁止用基金合同里的策略描述替代报告期内的运作说明
- **标题不匹配的章节一律标 `rejected_cross_document` 并整条丢弃**：同管理人、名称相近、同报告期的其他基金章节不得作为本基金证据；已误写入事实块则命中 `cross_document_recall`，结论判 `invalid` 并退回重做
- `not_retrievable` / `rejected_cross_document` 涉及的对照项（说的 vs 做的、上期说的 vs 本期做的）直接标记"无法对照"，并把对应字段列入 `missing_fields`；依赖它的结论强度由 `devils_advocate` 下调
- `clause_consistency_findings` 只列「条款原文 / 观测值 / 是否落在约束内」，不写"违规"等定性判断；**条款分母与观测分母不一致时标 `分母口径不一致，不判定`**，不得直接比较

## 禁止

- 不得评价管理人诚信、能力或措辞质量
- 不得把管理人的市场展望当作 FAMAS 的观点或预测
- 不得把报告全文、财务明细打包落库或再分发（运行时读取，读而不存）
- 不得把季报当成含审计意见的年报来读
- 不得用报告文字替代 `performance_metrics` 的定量计算
