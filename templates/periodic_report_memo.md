## 基金定期报告阅读备忘 — {{ periodic_report.report_type }} {{ periodic_report.report_period }}

**基金**：{{ fund_profile.fund_code }} {{ fund_profile.fund_name }} · **披露日期**：{{ periodic_report.disclosure_date }} · **视角**：{{ envelope.lens }}

### 数据说明
- 报告来源：{{ provenance(periodic_report.source_doc) }}
- 报告期：{{ periodic_report.report_period }}（**报告期末快照，非实时**）
- 审计状态：{{ periodic_report.caveats }}
- 未披露章节（`not_disclosed`）：{{ periodic_report.not_disclosed_sections }}
- 检索不可达章节（`not_retrievable`）：{{ periodic_report.not_retrievable_sections }}

### 核心风险提示（前置）
- 本备忘为**披露文档的事实摘录与对照**，不构成投资建议
- 管理人表述仅代表其当期观点，不代表 FAMAS 判断，也不预示后续表现
- {{ synthesis.key_risks }}

### 一、管理人报告（原文摘录）
- 报告期内投资策略与运作分析：{{ periodic_report.manager_strategy_text }}
- 业绩说明：{{ periodic_report.manager_performance_commentary }}
- 后市展望：{{ periodic_report.manager_outlook }}

> 原文定位：{{ periodic_report.quoted_excerpts }}

### 二、投资组合报告
- 资产组合：{{ periodic_report.portfolio_asset_mix }}
- 行业配置：{{ periodic_report.sector_allocation_in_report }}
- 主要持仓：{{ periodic_report.top_holdings_in_report }}
- 债券与衍生品敞口：{{ periodic_report.bond_and_derivative_exposure }}

### 三、财务报表与审计
- 主要财务项目：{{ periodic_report.financial_statement_items }}
- 报告内费用明细：{{ periodic_report.fee_detail_in_report }}
- 审计意见（仅年报）：{{ periodic_report.auditor_opinion }}

### 四、份额、持有人与重大事项
- 份额与持有人变动：{{ periodic_report.share_and_holder_changes }}
- 重大事项：{{ periodic_report.material_events }}

### 五、三类对照（只报差异）
| 对照 | 结果 |
|---|---|
| 说的 vs 做的 | {{ periodic_report.clause_consistency_findings }} |
| 上期说的 vs 本期做的 | {{ periodic_report.cross_period_narrative_diff }} |
| 合同条款 vs 实际运作 | {{ periodic_report.clause_consistency_findings }} |

### 六、反证与四段式判断
- 最薄弱假设与反证：{{ counter_evidence.weakest_assumptions }} / {{ counter_evidence.counter_signals }}
- 替代解释：{{ counter_evidence.alternative_explanations }}
- 置信度上限：{{ counter_evidence.confidence_cap }}
- 核心假设：{{ synthesis.hypothesis }}
- 支持证据：{{ synthesis.evidence_refs }}
- 失效条件：{{ synthesis.invalidation_conditions }}

### 七、数据缺口与来源分歧
- 未取到字段：{{ envelope.missing_fields }}
- 来源分歧：{{ envelope.source_conflicts }}

---
{{ fixed_disclaimer }}
