# cost_model — 成本模型（事实层）

> `layer: fact` · 无 persona · 所有估算必须透明 · 输出块见 `contracts/famas.contract.json#/blocks/cost_model`

## 输入

`fund_code` · `horizon`（持有年数）· 可选 `compare_codes`（份额类别 / ETF 联接对比）

## 语义字段

`fee_schedule` `turnover_history` `scale_history` `trading_costs` `fund_classification`

## 计算口径

| 项目 | 口径 |
|---|---|
| 显性费率 | 管理费 + 托管费 + 销售服务费（年化）；申购/赎回按持有期档位计入一次性成本 |
| 隐性成本 | 换手率 × 单边交易成本假设（冲击成本 + 买卖价差）；**必须列出假设参数与来源**，输出标 `estimated: true` |
| 假设驱动字段 | `trading_costs` 属 `assumption-driven`，允许没有直接数据源。不可得时使用 `assumptions` 中的默认参数计算，标 `estimated: true` 并在 `missing_fields` 中提示；**不得把估算写成实测**，也不得用模型记忆编造参数 |
| 总持有成本 TCR | 1/3/5 年累计显性 + 隐性 + 申赎；给出公式与逐年明细 |
| 成本侵蚀比例 | TCR / 同期毛收益（毛收益口径需与 `performance_metrics` 一致） |
| 同类对比 | 同类基金 TCR 中位数、本基金分位；标注同类划分标准 |
| 规模 | 当前规模、近 4 季变化；>100 亿标「策略容量阈值提示」、<2 亿标「清盘线阈值提示」，**仅标阈值，不预测发生** |
| QDII 附加 | 汇率对冲成本、海外托管费、其他附加费（若适用） |

## 份额类别 / 场内场外临界点（供 `research/share_class_breakeven` 复用）

对同一策略的多个份额或「场内 ETF vs 场外联接」：

```
TCR_A(h) = 申购费_A + h × 年费_A + 赎回费_A(h)
TCR_C(h) = 销售服务费_C × h + 赎回费_C(h)
breakeven_h = 使 TCR_A(h) = TCR_C(h) 的最小 h（无解析解时按 0.25 年步长数值求解）
```

输出：各方案逐年 TCR 表、临界持有期、临界点附近敏感性。**临界点不是持有建议**。

## 输出要求

- 结构化输出 `cost_model` 块；每个数值带 `source`、`as_of`、`estimated` 标记
- 所有假设参数集中在 `assumptions` 子块列出，便于复核
- 同类分位须说明样本范围与剔除规则

## 禁止

- 不得输出"费率划算/太贵""建议选 A 类"等评价或选择建议
- 不得把隐性成本估算写成实测数据
- 不得忽略赎回费随持有期递减的档位差异
