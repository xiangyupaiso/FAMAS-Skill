# 反证引擎细则

> 供 `capabilities/devils_advocate.md` 执行。目标不是"唱反调"，是**找出这个判断最可能错在哪**。

## 一、五类模式检查清单

| 模式 | 必检项 | 数据来源 |
|---|---|---|
| ① 数据口径 | 复权方式、报告期、份额类别、样本窗口变化后结论是否翻转；季报快照代表性；净值/持仓是否同期 | `performance_metrics`、`periodic_report` |
| ② 基准与归因 | 换一组业绩基准、剥离风格 β 后超额是否消失；收益是否来自行业 β 而非选股；同类分位口径 | `performance_metrics.alpha_alt_benchmark`、`index_quotes` |
| ③ 时间稳定性 | 1/3/5 年与滚动 12 月窗口结论是否一致；是否由单一极端区间驱动；回撤修复是否未完成 | `performance_metrics.rolling_stability` |
| ④ 结构性 | 规模突破容量阈值、跌破清盘线、经理变更、持有人集中、风格漂移超阈值 | `cost_model.scale_assessment`、`people.roster_changes` |
| ⑤ 替代解释 | 同一组事实能否被更朴素的假设解释（板块行情 vs 经理能力；份额类别差异 vs 策略差异） | 全部事实块 |

每类都要输出 `checked` / `finding` / `evidence_ref`；无发现写 `none_found_and_why`，并说明检索了哪些字段。

## 二、反证强度与置信度上限

| 反证强度 | 判定 | `confidence_cap` |
|---|---|---|
| `none` | 五类均无实质发现，关键字段齐全 | `strong` |
| `minor` | 1 条可解释反证，或次要字段缺失 | `moderate` |
| `material` | 未解释反证 / 关键字段缺失 / 多源分歧 / 换基准后超额消失 | `weak` |
| `fatal` | 任一否决项命中且无法解释 | `invalid` |

`synthesis` 的结论强度**不得超过** `confidence_cap`；`weak` / `invalid` 时禁止输出星级与适配度分档。

## 三、反证的证据要求

```
合格： "近 3 年超额 +4.2%，但换用中证 800 作基准后降至 +0.3%
        （来源：performance_metrics.alpha_alt_benchmark，as_of 2026-09-30）"
不合格： "市场风格可能变化，需谨慎"
不合格： "某研报认为该基金超额不可持续"（研报观点只能作 opinion_ref）
```

- 每条反证必须指向具体事实块字段，带 `source` + `as_of`
- 缺字段导致无法检验的方向写入 `missing_evidence`，不猜、不跳过
- 不得修改事实层数字；不得替 `synthesis` 下结论

## 四、与失效条件的对应

每条 `material` 以上的反证都应转化为至少一个可观测的 `invalidation_condition`：

| 反证 | 失效条件示例 |
|---|---|
| 换基准后超额消失 | "若连续 2 季度相对合同基准超额为负，则能力假设作废" |
| 规模逼近容量阈值 | "若规模突破 100 亿，则策略一致性结论需重估" |
| 季报快照滞后 | "若下一期持仓行业分布较本期变动超过 X，则本期敞口结论作废" |

失效条件写入 `triggers/rules.yaml` 可监控的观测指标，供 `core/d_monitor` 后续巡检。

## 五、禁止

- 为凑数编造反证
- 把研报结论直接当反证
- 输出任何操作建议
- 在 `devils_advocate` 阶段就给出"最终结论"
