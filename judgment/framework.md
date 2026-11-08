# 四段式判断框架（2.0 完整规范）

> 结论的合法性来自结构，不来自措辞。任何一个结论缺少第 3 或第 4 段，判定为不合格输出，退回重做。

## 一、四段

```
1 核心假设  hypothesis
   本次判断依赖的关键前提，必须可被事实检验。
   例："季报持仓可代表当前敞口""经理能力圈稳定""费率结构未变更"。
   禁止写"市场长期向好"这类不可证伪的前提。

2 支持证据  evidence_refs
   指向具体事实块字段，逐条带 source + as_of + confidence。
   禁止写"综合来看表现良好"这类无指针的概述。

3 反证      counter_evidence
   必须引用 capabilities/devils_advocate 输出的 counter_evidence 块。
   至少包含：最薄弱假设、一条反证信号、一条更朴素的替代解释。
   无反证发现也要写 none_found_and_why 并说明检索范围。

4 失效条件  invalidation_conditions
   "当 X 出现时本结论作废"，X 必须可观测、可触发、能与 triggers/rules.yaml 对齐。
   禁止写"若市场发生极端变化"这类无法监测的条件。
```

## 二、一票否决优先于加权评分

真实投委会不把维度打分求平均。评分允许存在，但必须：

```
先跑 judgment/veto-rules.yaml 的全部否决项
  -> 任一命中：结论显式降级或标注"前提不成立"，不得被其他维度高分抵消
  -> 全部未命中：才进入加权评分，且必须写明权重、口径与样本窗口
```

## 三、结论强度分级（受 confidence_cap 约束）

`devils_advocate` 输出 `confidence_cap`，`synthesis` 的结论强度不得超过它：

| 等级 | 允许的表述 | 触发条件 |
|---|---|---|
| `strong` | 可以给出明确适配度分档 | 五类反证均无实质发现，且关键字段齐全 |
| `moderate` | 适配度需附条件限定 | 存在 1 条可解释反证，或次要字段缺失 |
| `weak` | 只输出"需关注的观测指标" | 存在未解释反证、关键字段缺失、多源分歧或否决项命中 |
| `invalid` | 明确写"前提不成立，本轮不下结论" | 否决项命中且无法解释；**含跨文档误召回未被剔除、基准版本错配导致跨期对照失效** |

**禁止**：在 `weak` / `invalid` 下仍输出星级或适配度分档。

## 四、常见失败模式（自检）

| 失败 | 表现 | 修正 |
|---|---|---|
| 结论先行 | 先有判断再找证据 | 强制先跑反证引擎，再进 synthesis |
| 事后归因 | 用结果倒推原因 | 把"替代解释"列为必填项 |
| 基准错配 | 用沪深 300 当所有基金的基准 | `performance_metrics.benchmark_used` 必须来自合同基准 |
| 快照当实时 | 季报持仓写成"当前持仓" | 模板强制标注报告期与滞后性 |
| 语料冒充结论 | 直接搬运研报观点 | 观点只能作 `opinion_ref` 证据，见 `institutional-input.md` |
| 空泛反证 | "市场有不确定性" | 反证必须引用具体事实块字段 |
| 越界 | 输出操作建议 | `policies/compliance.md` 输出前拦截 |
| 基准版本错配 | 报告期内基准已变更，却用新基准回算旧区间 | `benchmark_used` 必须带生效日；跨版本对照标 `benchmark_version_break` 并降 weak |
| 文档身份未校验 | 把同管理人/名称相近基金的 §4.4 原文当作本基金证据 | 逐条校验 `title`，不匹配标 `rejected_cross_document`，命中否决项直接判 invalid |

## 四点五、文档不可达 / 误召回的降级规则（2026-11-07 补测）

| 状态 | 含义 | 处置 |
|---|---|---|
| `not_disclosed` | 该报告类型按披露规则本就不含此章节（如季报无审计意见） | 正常记录，不影响结论强度 |
| `not_retrievable` | 目标文档的该章节在本次检索中未命中 | 依赖它的对照标「无法对照」，字段进 `missing_fields`，`confidence_cap` 最多 `moderate` |
| `rejected_cross_document` | 检索命中了章节，但标题指向其他基金/其他报告期 | **整条丢弃**；若已写入事实块 → 命中 `cross_document_recall`，结论判 `invalid` 并退回重做 |
| `second_hand` | 新闻中转载的研报观点 | 只能作 `opinion_ref`，标 L3 + 需核实原文，不进数值结论 |

`not_retrievable` 与 `rejected_cross_document` 都必须写入 `periodic_report.not_retrievable_sections` 的伴随说明，禁止用合同层面的策略描述（§2）冒充报告期运作说明（§4.4）。

## 五、与定期报告阅读的关系

`capabilities/periodic_report_reader.md` 提供的三类对照（说的 vs 做的、上期说的 vs 本期做的、合同 vs 实际）是反证引擎的一手输入：**管理人表述本身不是结论，是待检验的假设**。这把"读报告"和"有专业度"接成了同一条链路，而不是两个功能。
