## 决策备忘 — {{ envelope.workflow_id }}

**生成时间**：{{ envelope.generated_at }} · **视角**：{{ envelope.lens }} · **关联报告**：{{ envelope.inputs.report_ref }}

> 本模板承载四段式判断框架。它是 v2.0 已预留的 v2.0 接口：结构现在就生效，决策日志校准与机构语料引用在 v2.0 接入。

### 数据说明
- 全部引用字段的来源、时点、等级见各 `evidence_refs` 标注
- 数据缺口与分歧在文末统一列出

### 核心风险提示（前置）
{{ synthesis.key_risks }}
{% if synthesis.veto_checks.triggered %}
- **前提不成立（一票否决）**：{{ synthesis.veto_checks.triggered }}
{% endif %}

### 一、问题与边界
- 本次要回答的问题：{{ envelope.inputs.question }}
- 不在本次范围内：{{ envelope.inputs.out_of_scope }}
- 数据时点与市场状态：{{ envelope.inputs.market_state }}

### 二、四段式判断
| 环节 | 内容 |
|---|---|
| 核心假设 | {{ synthesis.hypothesis }} |
| 支持证据 | {{ synthesis.evidence_refs }} |
| 反证（最薄弱假设） | {{ synthesis.counter_evidence }} |
| 失效条件 | {{ synthesis.invalidation_conditions }} |

### 三、一票否决项检查
{{ synthesis.veto_checks }}

### 四、适配度结论（非推荐度）
- 对 {{ synthesis.suitable_for }} 的适配度：{{ synthesis.adaptability }}
- 不适合：{{ synthesis.unsuitable_for }}
- 风险等级 / 持有期：{{ synthesis.risk_level }} / {{ synthesis.horizon_fit }}

### 五、条件化关注框架
> 以"若 X 出现则本结论需重估"的形式给出可观测量，不给操作指令。

{{ synthesis.invalidation_conditions }}

### 六、机构观点引用（仅证据，不作结论）
{% for r in synthesis.opinion_refs %}
- {{ r.institution }} · {{ r.published_at }} · {{ r.title }} — {{ r.claim }}（非一手来源，需核实原文）
{% endfor %}

### 七、决策记录（v2.0 校准用）
- 记录 ID：{{ synthesis.decision_log_ref }}
- 待季度回看项：{{ synthesis.invalidation_conditions }}

### 八、数据缺口与来源分歧
- 未取到字段：{{ envelope.missing_fields }}
- 来源分歧：{{ envelope.source_conflicts }}

---
{{ fixed_disclaimer }}
