# synthesis — 综合层（唯一允许输出观点的能力）

> `layer: synthesis` · 必须作为最后一个业务步骤 · 前置必须有 `devils_advocate` · 输出前强制经过 `policies/compliance.md` 全项检查
> 输出块见 `contracts/famas.contract.json#/blocks/synthesis` · 判断规范见 `judgment/framework.md`

## 定位

事实层给的是"数字是什么"，判断层给的是"这个判断最可能错在哪"，本能力回答"这些数字意味着什么、在什么条件下不成立"。**专业度体现在判断结构，不在措辞风格**：不模仿研报语气，不堆砌术语，不给出比证据更强的结论。

## 输入

`upstream_blocks`（本次 DAG 产出的全部事实块）· `counter_evidence`（来自 `devils_advocate`）· `lens`（默认 `retail`，定义见 `judgment/lenses.yaml`）

## 一、四段式判断框架（所有结论必须齐备）

```
1. 核心假设   hypothesis       本次判断依赖的关键前提（如"经理能力圈稳定""季报持仓可代表当前敞口"）
2. 支持证据   evidence_refs    指向具体事实块的字段，带 source + as_of
3. 反证       counter_evidence 必须引用 devils_advocate 输出的 counter_evidence 块：
                               最薄弱假设 + 至少一条反证信号 + 一条更朴素的替代解释
4. 失效条件   invalidation     "当 X 出现时本结论作废"，必须可观测、可触发（与 triggers/rules.yaml 对齐）
```

任何一个结论缺第 3 或第 4 项，视为不合格输出，退回重做。**反证段不得由本能力自行编写**；`devils_advocate` 输出为空时不得进入本能力。

## 二、一票否决优先于加权评分

真实投委会不是把维度打分求平均。完整规则与阈值见 `judgment/veto-rules.yaml`，以下任一项触发时，综合结论必须显式降级或标注"前提不成立"，不得被其他高分抵消：

| 否决项 | 触发来源 |
|---|---|
| 规模跌破清盘线阈值（<2 亿） | `cost_model.scale_assessment` |
| 基金经理离任 / 共管关系重大变化 | `people.roster_changes` |
| 风格漂移超出历史中枢（默认 1σ） | `performance_metrics.style_drift_distance` |
| 规模突破策略容量阈值（>100 亿） | `cost_model.scale_assessment` |
| 关键字段大面积缺失 | `envelope.missing_fields` |
| 多源数据存在未解释分歧 | `envelope.source_conflicts` |
| 报告观测值落在合同约束之外 | `periodic_report.clause_consistency_findings`（只标需关注，不下法律判断） |

**评分允许存在，但必须在否决项检查之后**，且说明权重与口径。结论强度不得超过 `counter_evidence.confidence_cap`；`weak` / `invalid` 时禁止输出星级与适配度分档。

## 三、lens 视角切换

同一批事实块，按 `lens` 换结论框架，不改数字。视角定义在 `judgment/lenses.yaml`（新增视角只需加一段，不改本能力）：

| lens | 关注点 | 输出框架 |
|---|---|---|
| `retail`（默认） | 适配度、风险等级、持有期 | 适配投资者类型 + 风险提示 |
| `fund_manager` | 能力圈、风格漂移、策略容量、叙事一致性 | 策略一致性检验 + 容量约束 |
| `fof` | 组合边际贡献、替代性、相关性、拥挤度 | 相对现有组合的边际贡献 |
| `risk` | 回撤、集中度、流动性、适当性、条款一致性 | 风险敞口清单 + 阈值监控项 |
| `advisor` | 适当性、话术边界、需披露事项 | 沟通要点 + 禁止表述清单 |

## 四、输出框架

- **适配度，不是推荐度**：表述为"该基金对 XX 类型投资者的适配度"，维度为风险等级、持有期、资金属性
- **时机矩阵**：只描述估值分位等客观状态与不同资金属性下的差异，不给"入场"指令
- **星级**（若工作流要求）：必须附评级依据、各维度得分、否决项检查结果与置信度上限
- **风险提示前置**：结论之前先给核心风险
- **免责声明**：使用 `policies/compliance.md` 中的固定文案，不自行改写

## 五、v2.0 判断层（已实装）

v2.0 只预留接口，v2.0 已全部落地，本能力直接消费：

| 层 | 实装位置 | 本能力如何使用 |
|---|---|---|
| L1 判断框架 | `judgment/framework.md`、`judgment/veto-rules.yaml` | 四段式 + 一票否决 + 结论强度分级 |
| 反证引擎 | `capabilities/devils_advocate.md`、`judgment/devils-advocate.md` | `counter_evidence` 段的唯一来源，提供 `confidence_cap` |
| L2 决策记忆 | `judgment/decision-log.schema.json`、`judgment/calibration.md` | `decision_log_ref` 关联历史判断，供 `judgment/quarterly_calibration` 回看 |
| L3 机构语料 | `judgment/institutional-input.md` | `opinion_refs` 只作背景证据，运行时检索、读而不存，绝不进结论段 |
| L4 视角 | `judgment/lenses.yaml` | `lens` 参数读取，扩展不改能力单元 |

## 禁止

- 输出"买入 / 卖出 / 加仓 / 减仓 / 清仓"及任何等价指令
- 输出"推荐 / 不推荐""建议配置 X%"
- 输出具体买卖价位、目标价、收益预测
- 引用未经 `data/gateway.md` 取数的事实
- 把研报观点或管理人表述写成自己的结论；引用须带 `opinion_ref` 与来源
- 自行编写反证段、绕过 `confidence_cap` 提高结论强度
- 自行改写、缩减或省略标准免责声明
