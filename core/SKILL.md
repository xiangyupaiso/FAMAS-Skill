---
name: "famas"
version: "2.0.0"
description: "FAMAS 基金分析决策支持系统的唯一逻辑入口。分析基金、基金评级、筛选基金、对比基金、诊断持仓、组合再平衡、基金监控预警、定投适配、换基金评估、份额选择、读季报/半年报/年报、研报观点核对、结论压力测试、季度校准、多源数据校验等场景，统一由本入口路由到声明式工作流。"
---

# FAMAS Core — 唯一逻辑源

> **版本**: v2.0.0（v2.0 架构层 + v2.0 判断层；目录名保留 `FAMAS-Skill-v2.0` 仅为路径兼容）
> **定位**: 面向个人投资者的基金分析、筛选、诊断与持续监控决策支持系统
> **唯一逻辑源声明**: 本文件是 FAMAS 全部执行逻辑的唯一定义处。`.trae/`、`.claude/`、`.agents/` 下的三份 SKILL.md 只是平台薄适配层，**不得复制、改写或缓存本文件的流程**。任何行为变更只改本文件及其引用的 `core/`、`workflows/`、`judgment/`、`policies/`、`data/`。

---

## 一、加载顺序（按需加载，禁止一次性灌入上下文）

Core 常驻；其余文件只在被路由命中时读取，避免上下文膨胀。

| 顺序 | 文件 | 何时读 |
|---|---|---|
| 1 | `core/SKILL.md` | 常驻，每次触发必读 |
| 2 | `core/router.md` | 每次触发，用于意图判定 |
| 3 | `workflows/<命中工作流>.yaml` | 路由命中后 |
| 4 | `core/capability-registry.yaml` | 解析工作流中的 `use` 前 |
| 5 | `capabilities/<命中能力>.md` | 逐个能力执行前，读完即释放 |
| 6 | `data/gateway.md` + `data/semantic-fields.yaml` | 首次取数前 |
| 7 | `data/providers/<命中厂商>.yaml` | 选定数据源后 |
| 8 | `contracts/famas.contract.json` | 组装输出时 |
| 9 | `judgment/framework.md` + `devils-advocate.md` + `veto-rules.yaml` + `lenses.yaml` | **仅当 DAG 含 `devils_advocate` 或 `synthesis` 时** |
| 10 | `judgment/institutional-input.md` / `decision-log.schema.json` / `calibration.md` | 仅判断层对应工作流命中时 |
| 11 | `templates/<工作流指定模板>.md` | 渲染时 |
| 12 | `policies/compliance.md` + `policies/source-trust.md` + `policies/forbidden-words.txt` + `tools/check_report.py` | **输出前最后一步，必读**；渲染产物须过输出闸才能交付 |

---

## 二、Core 的四个职责

1. **意图路由**：把用户一句话映射为 `workflow_id + 参数 + lens`，规则见 `core/router.md`。
2. **能力注册与校验**：所有 `use` 必须在 `core/capability-registry.yaml` 中登记；未登记的能力一律拒绝执行并说明，不得临时杜撰角色。
3. **编排执行**：串行、并行、条件分支、循环、include、降级，规则见 `core/orchestrator.md`。
4. **合规与溯源闸**：所有输出在交付前统一经过 `policies/compliance.md` 的检查清单，禁止词扫描、风险提示、免责声明、来源标注在此一处完成。能力单元与工作流**不得自行定义合规条款**。

---

## 三、执行协议（每次触发固定七步）

```
Step 1  解析意图 → router.md 得到 workflow_id 与参数；参数缺失时按工作流 inputs 逐个追问（一次问完）
Step 2  读取工作流 YAML → 展开 include → 生成执行 DAG；若用户指定了部分能力/维度，按 orchestrator 的"临时拼装"规则裁剪 DAG
Step 3  对每个 use，先在注册表校验 id、inputs、requires、trust_min，再读取对应 capabilities/*.md
Step 4  取数：向 data/gateway.md 声明语义字段，由网关探测可用 MCP 并路由；任何数字必须带 source / as_of / confidence
Step 5  读文档：命中报告类工作流时由 periodic_report_reader 读季报/半年报/年报；章节片段先做 document_title_match 校验，标题/报告期不匹配标 rejected_cross_document 整条丢弃；只做原文摘录与三类对照，读而不存
Step 6  判断：devils_advocate 六类反证（含来源身份）→ veto-rules 一票否决（含跨文档误召回、基准版本变更）→ synthesis 四段式结论；字段一律以 contracts/famas.contract.json 为准
Step 7  过闸：policies/compliance.md 全项检查 → 按 templates/ 渲染 → tools/check_report.py 输出闸扫描（禁止词 + 免责声明 + 溯源 + 口径 + 文档身份 + 基准版本）→ 交付
```

**禁止**：跳过 Step 7；在能力单元里写"我认为/建议买入"；用模型记忆填补未取到的数值；把密钥写入任何被提交的文件；在 `synthesis` 里自行编写反证段。

---

## 四、能力分层（角色冗余的根治）

| 层 | 能力 | 允许输出 |
|---|---|---|
| 事实层 `layer: fact` | `fund_profile` / `performance_metrics` / `cost_model` / `people` / `macro_context` / `universe_scan` / `relative_compare` / `portfolio_view` / `periodic_report_reader` | **只有事实、计算与原文摘录**，无观点、无预测、无评价性措辞 |
| 判断层 `layer: judgment` | `devils_advocate` | 只输出反证清单、最薄弱假设、替代解释、置信度上限与失效条件，**不下结论** |
| 综合层 `layer: synthesis` | `synthesis` | 允许综合判断，但框架为"适配度"而非"推荐度"，结论强度受 `confidence_cap` 约束 |

事实层与判断层能力**没有 persona、没有 System Prompt 人设**，只有输入、口径、输出 schema。原 v1 的 `watchtower` 不是 Agent，已降格为 `triggers/rules.yaml` 中的调度器 + 阈值规则集。

### 定期报告是必须读的文档

基金的季度报告 / 中期报告（半年报） / 年度报告不是"持仓数据的来源标签"，而是**被阅读的对象**。`periodic_report_reader` 按报告类型区分必读章节：季报不推定存在财务报表或审计意见，中期报告标明是否未经审计，年报照录审计意见原文；并做三类对照（说的 vs 做的、上期说的 vs 本期做的、合同条款 vs 实际运作）。管理人表述是**待检验的假设**，不是结论。

---

## 五、数据源规则（MCP 层）

- Core 与工作流**只认语义字段**（如 `fund_nav`、`fee_schedule`、`periodic_report_full`、`manager_commentary`），**不认任何厂商工具名**。
- 厂商工具名由 `data/gateway.md` 在运行时通过 `tools/list` 探测，映射表只声明"能力类别提示"，不硬编码端点与工具名。
- 登录与授权由宿主客户端完成（OAuth 2.1 + PKCE 或 API Key）。**FAMAS 没有账号、没有登录入口；要登录的是数据源的 MCP**。Skill 不能替用户登录，也不持有任何密钥。未连接时按 `policies/source-trust.md` 降级并给出 `SETUP.md` 的一次性引导，不得静默改用模型记忆。
- 可信度分级与冲突处理统一见 `policies/source-trust.md`；同一指标多源不一致时列分歧，不静默取一个。
- 研报与报告全文按授权在运行时读取，**读而不存**：不打包、不落库、不再分发。规范见 `judgment/institutional-input.md`。

---

## 六、降级与失败

| 情形 | 行为 |
|---|---|
| 意图不明确 | 按 `router.md` 的歧义规则给出候选工作流让用户选，不猜测 |
| 工作流未登记 | 尝试用已登记能力临时拼装 DAG；仍不成立则明确说明"该场景尚未定义" |
| 能力所需语义字段不可得 | 标记 `missing_fields`，跳过依赖该字段的计算，在报告中显式列出缺口，**不得用估算值伪装成数据** |
| 定期报告未披露某章节 | 标 `not_disclosed`，不推测、不把季报当年报读 |
| 反证引擎无发现 | 写 `none_found_and_why` 并说明检索范围，不为凑数编造反证 |
| 否决项命中 | 结论显式降级或标"前提不成立"，`weak` / `invalid` 时禁止输出星级与适配度分档 |
| MCP 未连接 / 401 / 限流 | 按可信度降一级重试，仍失败则输出"数据源未覆盖"并给出 `SETUP.md` 引导 |
| 全部数据源不可用 | 只输出分析框架与待补字段清单，不输出任何数值结论 |

---

## 七、合规硬约束（摘要，完整定义在 policies/compliance.md）

- 严禁输出"买入 / 卖出 / 加仓 / 减仓 / 清仓"等明确交易信号
- 输出框架为"该基金对 XX 类型投资者的适配度"，不是"推荐 / 不推荐"
- 所有评级、诊断输出必须前置风险提示，并附标准免责声明
- 所有关键数字必须可追溯到 来源 + 时点 + 口径
- 事实层能力不得夹带观点；研报、公告与管理人表述为证据，不是结论
- 报告类输出必须标注"报告期末快照，非实时"，且不得输出"违规/合规"等定性法律判断

---

> **合规声明**：本报告仅作信息整理与适配度分析，不构成投资建议。基金过往业绩不预示未来表现。市场有风险，投资需谨慎。
