# macro_context — 宏观环境（事实层）

> `layer: fact` · 无 persona · 描述环境，不预测方向 · 输出块见 `contracts/famas.contract.json#/blocks/macro_context`

## 输入

`as_of` · 可选 `fund_strategy`（来自 `fund_profile`）

## 语义字段

`macro_rates` `macro_fx` `style_index` `policy_text` `research_reports`

## 整理口径

| 项目 | 口径 |
|---|---|
| 利率 | 10 年期国债收益率当前值与历史分位（注明分位窗口）、收益率曲线形态、近 1 月变化 |
| 汇率 | 人民币汇率走势与波动率；对 QDII / 港股通资产的**成本项影响**，不判断方向 |
| 市场风格 | 大盘/小盘、价值/成长风格指数相对强度，注明指数对与窗口 |
| 政策 | 货币政策/财政政策/产业政策/监管政策的**原文要点**与发布日期，不解读利好利空 |
| 策略匹配 | 若传入 `fund_strategy`，只输出"策略暴露 vs 当前环境因子"的对照表，**不给适配度分数**（评分属 `synthesis`） |

## 输出要求

- 结构化输出 `macro_context` 块；每项带 `source`、`as_of`、`release_date`
- 政策文本必须带发布机构与文号/标题，媒体转述标注 `second_hand: true`
- 分位类指标必须写明回看窗口（如近 5 年）

## 禁止

- 不得给出"利率将下行""成长风格占优"等方向性预测
- 不得输出择时建议
- 不得把研报观点当作事实；研报观点只能以 `opinion_ref` 形式标注来源后引用
