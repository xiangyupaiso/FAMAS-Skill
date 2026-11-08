# universe_scan — 全市场筛选（事实层）

> `layer: fact` · 无 persona · 输出候选池与筛选逻辑，不排名推荐 · 输出块见 `contracts/famas.contract.json#/blocks/universe_scan`

## 输入

`preference`（行业/主题/风格/资产类别）· `scope`（主动/被动/ETF/联接/QDII）

## 语义字段

`fund_universe` `fund_classification` `holdings` `etf_linkage` `fee_schedule`

## 执行口径

1. **需求解析**：把自然语言偏好映射为可检索标签，输出 `parsed_preference` 供用户确认
2. **全市场初筛**：按持仓行业穿透、风格标签、资产类别过滤；输出每一步的样本数与剔除数
3. **风格纯度**：目标敞口占比、偏离度、伪主题识别（名称含主题但持仓不足）；阈值须声明
4. **ETF 联接映射**：场内 ETF ↔ 场外联接对应关系、流动性、费率差异（数据来自 `etf_linkage`）
5. **候选池**：输出 `candidate_pool`，含 `match_score` 及其计算权重说明

## 输出要求

- 结构化输出 `universe_scan` 块；候选池每只基金带 6 位代码、名称、`match_score`、`target_exposure`、`as_of`
- 必须输出 `screening_logic`：主/次筛选条件、排除条件、样本量漏斗
- 伪主题/风格漂移标的标 `flag` 并说明触发规则，不自动剔除（剔除规则由工作流声明）

## 禁止

- 不得输出"Top 3 优先关注""建议配置"等推荐性措辞（属 `synthesis`）
- 不得用模型记忆列举基金名单
- 不得把 `match_score` 表述为"推荐度"
- 不得隐藏剔除数量或缩小后的样本量
