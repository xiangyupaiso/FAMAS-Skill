# Core — 意图路由表

> 唯一职责：把用户的一句话变成 `workflow_id + 参数 + lens`。本文件不含执行流程、不含合规条款。

## 一、路由优先级

1. 用户显式点名工作流 ID 或命令（如 `/famas a_single_fund`）→ 直接命中
2. 意图词命中下表 → 取匹配度最高的一条
3. 复合意图 → 拆成多条工作流按序执行（见第三节）
4. 无法命中 → 尝试临时拼装；仍不成立则明确说明"该场景尚未定义"

## 二、意图 → 工作流映射

| workflow_id | 意图词 / 触发语 | 必填参数 | 分类 |
|---|---|---|---|
| `core/a_single_fund` | 分析基金、基金评级、这只基金怎么样、深度分析 | `fund_code` | 核心 |
| `core/b_screen` | 筛选基金、找基金、哪只基金、科技/红利/成长主题 | `preference` | 核心 |
| `core/c_portfolio` | 诊断持仓、组合诊断、再平衡、持仓体检 | `holdings` | 核心 |
| `core/d_monitor` | 监控基金、基金预警、异动提醒、设置巡检 | `watchlist` | 核心 |
| `lifecycle/suitability_check` | 我适合买吗、定投适配、风险测评、能不能配 | `fund_code` + `investor_profile` | 生命周期 |
| `lifecycle/fund_replacement` | 要不要换基金、换成哪只、替换评估、赎回换仓成本 | `held_fund` + `candidate_fund` | 生命周期 |
| `lifecycle/goal_backsolve` | 教育金、养老金、20 年后要用、目标反推、攒够 X 万 | `goal` + `horizon` | 生命周期 |
| `lifecycle/periodic_review` | 定期复查、季度体检、订阅复查、每月看一次 | `holdings` + `interval` | 生命周期 |
| `events/quarterly_holdings_review` | 季报解读、年报解读、重仓变化、经理说了什么做了什么 | `fund_code` + `report_period` | 事件 |
| `events/alert_reassessment` | 预警之后怎么办、重新评估、异动影响、要不要调整 | `alert_id` 或 `fund_code` + `alert_type` | 事件 |
| `events/corporate_action_impact` | 分红、拆分、限购、暂停申购、大额赎回条款影响 | `fund_code` + `event_type` | 事件 |
| `events/manager_change_impact` | 经理换了、基金经理离职、新增共管的影响 | `fund_code` + `change_event` | 事件 |
| `research/share_class_breakeven` | A 类还是 C 类、场内 ETF 还是场外联接、持有多久划算 | `fund_codes` + `horizon` | 深度研究 |
| `research/pseudo_diversification` | 伪分散、看着分散其实集中、真实相关性、持仓穿透 | `holdings` | 深度研究 |
| `research/skill_vs_luck` | 运气还是能力、超额稳不稳、基准换一个还成立吗 | `fund_code` + `lookback` | 深度研究 |
| `research/sponsor_concentration` | 同一家基金公司、管理人集中度、迷你基金清盘扫描 | `holdings` 或 `sponsor` | 深度研究 |
| `data-quality/cross_source_verify` | 数据对不上、两个平台数字不一样、核对一下、多源校验 | `fund_code` + `fields` | 数据质量 |
| `data-quality/provenance_audit` | 这个数字哪来的、报告溯源、出处审计、可信吗 | `report_ref` | 数据质量 |
| `events/periodic_report_deep_read` | 读季报、读半年报、中期报告、读年报、基金报告、定期报告、这份报告讲了什么 | `fund_code` + `report_type` + `report_period` | 事件 |
| `research/manager_narrative_drift` | 说的和做的一致吗、管理人表述、叙事漂移、上期说的现在还算数吗 | `fund_code` | 深度研究 |
| `research/report_consistency_check` | 有没有超仓位、符合合同吗、条款一致性、港股通权限用了吗、基准偏离 | `fund_code` + `report_period` | 深度研究 |
| `judgment/thesis_challenge` | 这个结论靠谱吗、压力测试、找反证、最薄弱假设、挑战一下这个判断 | `fund_code` | 判断层 |
| `judgment/quarterly_calibration` | 季度复盘、之前判断对不对、校准、决策日志、回看一下历史结论 | `decision_log_refs` + `review_period` | 判断层 |
| `judgment/institutional_evidence` | 研报怎么说、关键假设、机构观点、假设表回溯、卖方观点核对 | `fund_code` + `question` | 判断层 |

## 三、复合意图拆解

- "帮我对比这 3 只，但只看费率和经理稳定性" → 命中 `core/b_screen`，并按 `orchestrator.md` 的临时拼装规则把 DAG 裁剪为 `cost_model + people + relative_compare`。**不新增工作流**。
- "分析 020712 然后放进我的组合看看" → `core/a_single_fund` → `core/c_portfolio`，前者的输出作为后者 `holdings` 的补充输入。
- "上次那个预警，重新评估一下" → `events/alert_reassessment` 内部 `include: core/a_single_fund`，实现告警→重评估闭环。
- "把这份年报读了，再帮我压力测试一下里面的说法" → `events/periodic_report_deep_read` → `judgment/thesis_challenge`，管理人表述作为待检验假设进入反证引擎。

拆解后按序执行，每一步的输入输出以 `contracts/famas.contract.json` 为唯一契约。

## 四、参数抽取与追问

- `fund_code`：6 位数字；用户给名称时先经 `data/gateway.md` 的标识解析，无法确定则追问代码
- `holdings`：代码 + 权重，权重合计应为 100%；缺失时追问，不默认等权
- `investor_profile`：风险等级、投资期限、资金属性（一次性/定投）、可承受回撤；缺失时**一次问完**，不逐轮挤牙膏
- `report_type`：`quarterly` / `interim` / `annual`；用户只说"报告"时追问类型，**不默认按季报处理**
- `report_period`：`YYYYQn` / `YYYYH1` / `YYYY`，与 `report_type` 一致
- `horizon`：持有期，单位统一为年
- `lens`：可选，默认 `retail`；可取值见 `capabilities/synthesis.md`

## 五、歧义处理

| 情况 | 处理 |
|---|---|
| "科技基金怎么样" | 可能命中 `core/b_screen`（找科技基金）或 `core/a_single_fund`（分析某只）→ 给出两个候选让用户选 |
| "帮我看看我的基金" | 有持仓列表 → `core/c_portfolio`；只有单只代码 → `core/a_single_fund`；都没有 → 追问 |
| 命中多条且无优先级 | 列出候选，不猜测、不默认第一条 |

## 六、禁止

- 不得在路由阶段给出任何分析结论
- 不得因为"看起来像"就把基金名称当成基金代码
- 不得静默忽略用户指定的维度裁剪要求
