## 组合诊断报告

**工作流**：{{ envelope.workflow_id }} · **生成时间**：{{ envelope.generated_at }} · **视角**：{{ envelope.lens }}

### 数据说明
- 权重合计：{{ portfolio_view.weight_sum }}（{{ portfolio_view.weight_basis }}）
- 持仓报告期：{{ performance_metrics.report_period }}（季末快照，非实时）
- 相关性窗口：{{ portfolio_view.window }} · 样本数 {{ portfolio_view.sample_size }}

### 核心风险提示（前置）
- 本报告输出的是**风险敞口与适配度**，不是调仓方案
- 穿透计算依赖季报持仓，存在滞后与口径差异
- {{ synthesis.key_risks }}
{% if synthesis.veto_checks.triggered %}
- **前提不成立**：{{ synthesis.veto_checks.triggered }}
{% endif %}

### 一、组合概览
| 基金代码 | 名称 | 权重 | 类型 |
|---|---|---|---|
{% for h in envelope.inputs.holdings %}
| {{ h.fund_code }} | {{ h.fund_name }} | {{ h.weight }} | {{ h.fund_type }} |
{% endfor %}

### 二、穿透后资产配置
- 股票 / 债券 / 现金：{{ portfolio_view.asset_allocation }}
- 前三大行业（加权）：{{ portfolio_view.top_sectors_weighted }}
- 单只基金最大权重：{{ portfolio_view.max_fund_weight }}
- 穿透后前十大个股合计：{{ portfolio_view.top10_lookthrough_weight }} · HHI {{ portfolio_view.hhi }}

### 三、风格与相关性
- 风格暴露：{{ portfolio_view.style_exposure }}
- 相关系数矩阵：{{ portfolio_view.correlation_matrix }}
- 尾部相关：{{ portfolio_view.tail_correlation }}
- 表面分散实际集中识别：{{ portfolio_view.hidden_concentration }}

### 四、成本视角
- 组合加权 TCR：{{ cost_model.tcr_3y }} · 费率侵蚀：{{ cost_model.erosion_ratio }}
- 份额类别 / 场内场外临界点：{{ cost_model.breakeven_horizon }}

### 五、适配度与需关注事项（非调仓指令）
- 组合对 {{ synthesis.suitable_for }} 的适配度：{{ synthesis.adaptability }}
- 风险等级：{{ synthesis.risk_level }}
- 需持续关注的观测指标：{{ synthesis.invalidation_conditions }}

### 六、四段式判断
- 核心假设：{{ synthesis.hypothesis }}
- 支持证据：{{ synthesis.evidence_refs }}
- 反证：{{ synthesis.counter_evidence }}
- 失效条件：{{ synthesis.invalidation_conditions }}

### 七、数据缺口与来源分歧
- 未取到字段：{{ envelope.missing_fields }}
- 来源分歧：{{ envelope.source_conflicts }}

---
{{ fixed_disclaimer }}
