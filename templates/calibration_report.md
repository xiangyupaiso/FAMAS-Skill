## 决策日志季度校准报告 — {{ envelope.inputs.review_period }}

**生成时间**：{{ envelope.generated_at }} · **回看记录数**：{{ envelope.inputs.decision_log_refs | count }} · **视角**：{{ envelope.lens }}

### 数据说明
- 实际数据窗口：{{ performance_metrics.window }} — {{ provenance(performance_metrics.annual_return_3y) }}
- 报告期：{{ periodic_report.report_period }}（报告期末快照，非实时）
- 决策记录来源：本地授权记录，不上传、不入库

### 核心风险提示（前置）
- 校准是对**判断过程**的回看，不是对投资结果的评价，更不构成投资建议
- 历史判断的偏差可能来自数据、口径或框架任一层，不能简单归因于"看错方向"
- {{ synthesis.key_risks }}

### 一、逐条回看
| 记录 ID | 原假设 | 失效条件 | 是否触发 | 结论与实际偏离 | 误差来源分层 |
|---|---|---|---|---|---|
{% for r in decision_log.records %}
| {{ r.log_id }} | {{ r.hypothesis }} | {{ r.invalidation_conditions }} | {{ r.triggered }} | {{ r.deviation }} | {{ r.error_layer }} |
{% endfor %}

### 二、误差归因
- 数据层（缺失 / 滞后 / 多源分歧）：{{ envelope.missing_fields }} / {{ envelope.source_conflicts }}
- 口径层（复权、报告期、份额类别、窗口）：{{ decision_log.calibration_notes }}
- 框架层（假设过强、反证不足、置信度上限偏高）：{{ counter_evidence.weakest_assumptions }}

### 三、校准动作
- 更新的失效条件：{{ synthesis.invalidation_conditions }}
- 后续置信度上限：{{ counter_evidence.confidence_cap }}
- 需持续跟踪的观测指标：{{ counter_evidence.invalidation_conditions }}

### 四、反证与四段式
- 最薄弱假设：{{ counter_evidence.weakest_assumptions }}
- 替代解释：{{ counter_evidence.alternative_explanations }}
- 核心假设 / 支持证据 / 失效条件：{{ synthesis.hypothesis }} / {{ synthesis.evidence_refs }} / {{ synthesis.invalidation_conditions }}

### 五、数据缺口与来源分歧
- 未取到字段：{{ envelope.missing_fields }}
- 来源分歧：{{ envelope.source_conflicts }}

---
{{ fixed_disclaimer }}
