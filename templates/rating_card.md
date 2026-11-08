## 基金综合评级卡 — {{ fund_profile.fund_code }} {{ fund_profile.fund_name }}

**工作流**：{{ envelope.workflow_id }} · **生成时间**：{{ envelope.generated_at }} · **视角**：{{ envelope.lens }}

### 数据说明
- 数据时点：{{ provenance(fund_profile.fund_basic) }}
- 净值窗口：{{ performance_metrics.window }}，复权方式与缺失值处理见附录
- 季报持仓为季末快照，非实时；报告期 {{ performance_metrics.report_period }}

### 核心风险提示（前置）
{% for r in synthesis.key_risks %}
- {{ r.description }}（等级：{{ r.severity }}）— 观测指标：{{ r.monitoring }}
{% endfor %}
{% if synthesis.veto_checks.triggered %}
- **前提不成立**：以下一票否决项已触发 → {{ synthesis.veto_checks.triggered }}
{% endif %}

### 一、基础档案
- 类型 / 份额类别：{{ fund_profile.fund_type }} / {{ fund_profile.share_classes }}
- 业绩基准：{{ fund_profile.benchmark }}（权重 {{ fund_profile.benchmark_weights }}）
- 投资范围：{{ fund_profile.investment_scope }}；股票仓位 {{ fund_profile.stock_position_range }}
- 最新规模 / 在任经理：{{ cost_model.current_scale }} / {{ people.managers }}
- 特殊条款：{{ fund_profile.special_clauses }}

### 二、适配度结论（非推荐度）
{% for a in synthesis.adaptability %}
- {{ a.investor_type }}：适配度 {{ a.fit_level }}，依据 {{ a.rationale }}
{% endfor %}
- 风险等级：{{ synthesis.risk_level }} · 适配持有期：{{ synthesis.horizon_fit }}
- 不适合：{{ synthesis.unsuitable_for }}

### 三、评级与依据
- 星级：{{ synthesis.star_rating }}（如工作流启用）
- 评级依据：{{ synthesis.rating_rationale }}
- 各维度得分与权重：{{ synthesis.rating_dimensions }}

### 四、时机矩阵（客观状态，非入场指令）
{{ synthesis.timing_matrix }}

### 五、四段式判断
- **核心假设**：{{ synthesis.hypothesis }}
- **支持证据**：{{ synthesis.evidence_refs }}
- **反证**：{{ synthesis.counter_evidence }}
- **失效条件**：{{ synthesis.invalidation_conditions }}

### 六、关键指标
| 指标 | 数值 | 来源 · 时点 · 等级 |
|---|---|---|
| 近 3 年年化收益 | {{ performance_metrics.annual_return_3y.value }} | {{ provenance(performance_metrics.annual_return_3y) }} |
| 相对基准超额 | {{ performance_metrics.alpha.value }} | {{ provenance(performance_metrics.alpha) }} |
| 最大回撤 | {{ performance_metrics.max_drawdown.value }} | {{ provenance(performance_metrics.max_drawdown) }} |
| 夏普 / 卡玛 | {{ performance_metrics.sharpe_ratio.value }} / {{ performance_metrics.calmar_ratio.value }} | {{ provenance(performance_metrics.sharpe_ratio) }} |
| 3 年总持有成本 | {{ cost_model.tcr_3y.value }} | {{ provenance(cost_model.tcr_3y) }} |
| 宏观适配参考 | {{ macro_context.strategy_exposure_table }} | {{ provenance(macro_context.bond_10y) }} |

### 七、数据缺口与来源分歧
- 未取到字段：{{ envelope.missing_fields }}
- 来源分歧：{{ envelope.source_conflicts }}

---
{{ fixed_disclaimer }}
