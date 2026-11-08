## 基金筛选 / 对比报告 — {{ universe_scan.parsed_preference }}

**工作流**：{{ envelope.workflow_id }} · **生成时间**：{{ envelope.generated_at }}

### 数据说明
- 全市场样本时点：{{ provenance(universe_scan.fund_universe) }}
- 持仓报告期：{{ relative_compare.report_period }}（季末快照，非实时）
- 同类划分口径：{{ universe_scan.screening_logic }}

### 核心风险提示（前置）
- 筛选结果为**匹配度**排序，不是推荐排序，不构成配置建议
- 历史业绩、风格标签与持仓数据均存在滞后性
- {{ synthesis.key_risks }}

### 一、筛选条件与样本漏斗
- 解析后的偏好：{{ universe_scan.parsed_preference }} · 范围：{{ universe_scan.scope }}
- 主/次筛选条件：{{ universe_scan.screening_logic }}
- 样本漏斗：{{ universe_scan.sample_funnel }}
- 排除条件与剔除数：{{ universe_scan.exclusion_criteria }}
- 匹配度评分权重：{{ universe_scan.match_score_weights }}

### 二、候选池
| 排名 | 基金代码 | 名称 | 匹配度 | 目标敞口占比 | 风格纯度 | 数据时点 |
|---|---|---|---|---|---|---|
{% for f in universe_scan.candidate_pool %}
| {{ f.rank }} | {{ f.fund_code }} | {{ f.fund_name }} | {{ f.match_score }} | {{ f.target_exposure }} | {{ f.style_purity }} | {{ f.as_of }} |
{% endfor %}

### 三、横向对比
- 排序依据（可量化）：{{ relative_compare.ranking_basis }}
- 收益风险矩阵：{{ relative_compare.return_risk_matrix }}
- 持仓重合矩阵：{{ relative_compare.overlap_matrix }}
- 3/5 年 TCR 差额：{{ relative_compare.tcr_diff }}
- 经理稳定性：{{ relative_compare.manager_stability_matrix }}

### 四、ETF 联接与同质化
- 场内 ↔ 场外映射：{{ universe_scan.etf_linkage_map }}
- 伪主题 / 风格漂移标记：{{ universe_scan.pseudo_theme_flags }}
- 同质化程度：{{ relative_compare.overlap_matrix }}（仅数值，不作分散性结论）

### 五、四段式判断（适配度框架）
- 核心假设：{{ synthesis.hypothesis }}
- 支持证据：{{ synthesis.evidence_refs }}
- 反证：{{ synthesis.counter_evidence }}
- 失效条件：{{ synthesis.invalidation_conditions }}

### 六、数据缺口与来源分歧
- 未取到字段：{{ envelope.missing_fields }}
- 来源分歧：{{ envelope.source_conflicts }}

---
{{ fixed_disclaimer }}
