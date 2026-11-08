# relative_compare — 横向对比（事实层）

> `layer: fact` · 无 persona · 输出对比矩阵，不给淘汰建议 · 输出块见 `contracts/famas.contract.json#/blocks/relative_compare`

## 输入

`fund_codes`（2–5 只）· 可选 `dimensions`（用户指定只看哪些维度）

## 语义字段

`fund_nav_history` `holdings` `fee_schedule` `manager_roster`

## 计算口径

| 维度 | 口径 |
|---|---|
| 收益风险 | 同窗口年化收益、最大回撤、夏普、卡玛；窗口与 `performance_metrics` 保持一致 |
| 持仓重合 | 前十大重仓股重叠数/加权重叠率、行业分布余弦相似度、风格相似度 |
| 成本 | 费率结构差异、3/5 年 TCR 差额、隐性成本差额 |
| 人员 | 任职年限、共管情况、稳定性评分（口径同 `people`） |
| 同质化 | 重合度矩阵 + 集中度指标，标注计算所用报告期 |

## 输出要求

- 结构化输出 `relative_compare` 块；每只基金必须带标准 6 位代码，逐一标注
- 排序必须给出**可量化依据**（写明所依据的指标与窗口），不得用"综合实力""绑定深度"等笼统词
- 用户指定 `dimensions` 时只计算指定维度，其余标 `not_requested`
- 每期持仓数据标注报告期，跨期比较需说明是否同期

## 禁止

- 不得输出"淘汰 / 保留 / 优选"等建议（属 `synthesis`）
- 不得把重合度直接等同于"分散不足"的结论
- 不得混用不同报告期的持仓做重合度计算
