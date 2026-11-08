## 基金监控预警报告 — {{ envelope.generated_at }}

**巡检范围**：{{ envelope.inputs.watchlist }} · **规则集**：triggers/rules.yaml · **间隔**：{{ envelope.inputs.check_interval }}

### 数据说明
- 本次巡检数据时点：{{ provenance(alert.observed_value) }}
- 上次 / 下次巡检：{{ envelope.inputs.last_check }} / {{ envelope.inputs.next_check }}

### 核心风险提示（前置）
- 预警描述的是**已观测到的事实与触发条件**，不是操作建议
- 季报类指标为季末快照，公告类以发布日为准
- 高优先级预警将自动触发 `events/alert_reassessment` 进行影响重评估

### 一、巡检概览
- 监控基金数：{{ envelope.inputs.watchlist | count }}
- 预警总数：{{ envelope.alerts | count }}（高 {{ envelope.alert_summary.high }} / 中 {{ envelope.alert_summary.medium }} / 低 {{ envelope.alert_summary.low }}）

{% for level in ["high", "medium", "low"] %}
### {{ level }} 优先级预警
{% for a in envelope.alerts if a.priority == level %}
#### {{ a.fund_code }} — {{ a.fund_name }}
- 预警类型：{{ a.alert_type }}
- 触发条件：{{ a.trigger_condition }}
- 观测值 / 基线：{{ a.observed_value }} / {{ a.baseline_value }} — {{ provenance(a.observed_value) }}
- 异动详情：{{ a.details }}
- 需关注的观测指标：{{ a.suggested_watch }}
{% endfor %}
{% endfor %}

### 二、闭环动作
- 已触发的重评估工作流：{{ envelope.inputs.reassessment_refs }}
- 未触发原因（如有）：{{ envelope.inputs.skipped_reason }}

### 三、数据缺口与来源分歧
- 未取到字段：{{ envelope.missing_fields }}
- 来源分歧：{{ envelope.source_conflicts }}

---
{{ fixed_disclaimer }}
