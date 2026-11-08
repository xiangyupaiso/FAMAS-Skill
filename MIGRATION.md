# MIGRATION — v1 → v2.0

> v1 保持不动，v2.0 是独立目录。本文给出逐项映射，便于老用户切换。

---

## 1. 九个入口 → 一个 Core

| v1 入口 | 位置 | v2.0 对应 |
|---|---|---|
| `famas-analyze-fund` | `.claude/skills/` | `core/router.md` → `core/a_single_fund` |
| `famas-screen-fund` | `.claude/skills/` | `core/router.md` → `core/b_screen` |
| `famas-diagnose-portfolio` | `.claude/skills/` | `core/router.md` → `core/c_portfolio` |
| `famas-monitor-fund` | `.claude/skills/` | `core/router.md` → `core/d_monitor` |
| `famas-analyze-fund` | `.agents/skills/` | 同上（不再需要 Codex 专属副本） |
| `famas-screen-fund` | `.agents/skills/` | 同上 |
| `famas-diagnose-portfolio` | `.agents/skills/` | 同上 |
| `famas-monitor-fund` | `.agents/skills/` | 同上 |
| `famas-fund-analysis` | `.trae/skills/` | `core/SKILL.md`（TRAE 薄适配指向它） |

v1 的 `.claude` 与 `.agents` 四对 SKILL.md 内容几乎逐字相同（单文件 diff 仅 1 行触发词差异），合计 698 行中 697 行重复。v2.0 三份适配层各约 20 行，**不含任何流程**。

## 2. 命令对照

| v1 Claude Code | v2.0 |
|---|---|
| `/famas-analyze-fund 020712` | `/famas 分析基金 020712` |
| `/famas-screen-fund 科技成长` | `/famas 筛选科技成长基金` |
| `/famas-diagnose-portfolio 020712(30%), 005911(25%)` | `/famas 诊断持仓 020712 30%, 005911 25%` |
| `/famas-monitor-fund 020712, 005911` | `/famas 监控 020712, 005911` |

Codex / TRAE 无需命令，直接自然语言；`core/router.md` 统一判定意图。也可直接点名工作流 ID。

## 3. 十个 Agent → 九个能力 + 一个调度器

| v1 Agent | v2.0 | 变化 |
|---|---|---|
| `prospectus_analyzer` | `capabilities/fund_profile.md` | 去掉 persona，改为字段 + 口径 |
| `performance_analyst` | `capabilities/performance_metrics.md` | 增加基准敏感性与方法披露 |
| `cost_analyzer` | `capabilities/cost_model.md` | 增加份额类别 / 场内场外临界点 |
| `manager_profiler` | `capabilities/people.md` | 明确只使用公开披露信息 |
| `macro_strategist` | `capabilities/macro_context.md` | 明确不预测方向、不给适配度分数 |
| `sector_screener` | `capabilities/universe_scan.md` | 输出匹配度排序而非推荐 |
| `fund_comparator` | `capabilities/relative_compare.md` | 移除"淘汰/保留建议"，只给对比矩阵 |
| `portfolio_doctor` | `capabilities/portfolio_view.md` | 移除"再平衡方案"，只给风险敞口 |
| `wealth_advisor` | `capabilities/synthesis.md` | 唯一允许出观点；四段式 + 一票否决 + lens |
| `watchtower` | `triggers/rules.yaml` | **降格**为调度器 + 阈值规则，不是 Agent |

事实层能力统一受「只输出事实、不得夹带观点 / 主观判断 / 预测」约束——这正是 v1 里 8 个 Agent 的实际定位，v2.0 不再给它们配人设。

## 4. 四条工作流 → 十八条

| v1 | v2.0 |
|---|---|
| Workflow A 单基金深度分析 | `workflows/core/a_single_fund.yaml` |
| Workflow B 行业/偏好筛选 | `workflows/core/b_screen.yaml` |
| Workflow C 组合持仓诊断 | `workflows/core/c_portfolio.yaml` |
| Workflow D 持续监控预警 | `workflows/core/d_monitor.yaml`（+ 高优先级告警自动 include 重评估） |

新增 14 条见 `README.md` 的「18 条工作流」表。全部为声明式 YAML，可 `include`、可覆盖参数、可被 Core 临时裁剪。

## 5. 行为差异（重要）

| 项目 | v1 | v2.0 |
|---|---|---|
| 合规位置 | README / AGENTS.md / TRAE SKILL.md / wealth_advisor.md 四处 | `policies/compliance.md` 一处，Core 输出前强制检查 |
| 免责声明 | 各模板各写一份 | 固定文案，模板用 `{{ fixed_disclaimer }}` |
| 字段定义 | 4 份模板 + 4 份 md 重复，字段不一致 | `contracts/famas.contract.json` 单一契约 |
| 数据来源 | `pip install akshare`，无溯源 | 语义字段 → MCP 网关；每个数字带 source / as_of / confidence |
| 数据缺口 | 可能用模型记忆填补 | 显式 `missing_fields`，禁止填补 |
| 多源冲突 | 未定义 | `policies/source-trust.md`：列分歧，不静默取一个 |
| 输出观点 | 事实层 Agent 偶尔越界 | 仅 `synthesis` 可出观点，其余由合规闸拦截 |
| 定时监控 | 文档写"定期巡检"但未实现 | 宿主调度器触发，Skill 不常驻、不持有定时器 |

## 6. 迁移步骤

1. 保留 v1 目录不动（可继续用旧命令）
2. 把 `FAMAS-Skill-v2.0/` 放到工作区
3. 按 `SETUP.md` 完成一次数据源授权；**不登录也能用**，只是会输出分析框架与待补字段清单，不给数值结论
4. 用自然语言替换旧命令；或先跑「检查一下数据源」做首启自检
5. 如需回退，删除 v2.0 的入口文件即可，v1 完全不受影响

## 7. v1 已知问题（v2.0 已规避）

- 外网 README 美化时删除了「合规约束」「迭代路线图」「贡献指南」整章 → v2.0 合规进代码层策略文件
- README 标 v2.1、`SKILL.md` 标 v1.0，版本不一致 → v2.0 统一在 `core/SKILL.md` 与 `README.md` 标 2.0.0
- `[MIT](LICENSE)` 指向不存在的文件 → v2.0 已补 `LICENSE`
- `.claude` / `.agents` 内容重复 → 单一逻辑源
- 本地工作区曾出现 9 个文件被删除（8 个 skill + 宣传文案）→ v2.0 仓库自带 `.gitignore`，且入口不依赖被删文件

---

## 8. v2.0 → v2.0（本版本，目录名不变）

内容版本升到 **2.0.0**，但目录仍叫 `FAMAS-Skill-v2.0`，**只为路径兼容**；不另起一份重复仓库（避免回到 v1"同一份逻辑复制 5 遍"的老问题）。

| 项目 | v2.0 | v2.0 |
|---|---|---|
| 工作流 | 18 条 / 5 类 | **24 条 / 6 类**（新增 `judgment` 分类） |
| 能力 | 8 事实层 + 1 综合层 | **9 事实层 + 1 判断层 + 1 综合层** |
| 语义字段 | 28 | **38**（新增 10 个定期报告类字段） |
| 契约块 | 10 | **13**（+ `periodic_report` / `counter_evidence` / `decision_log`） |
| 模板 | 5 | **7**（+ `periodic_report_memo` / `calibration_report`） |
| 判断层 | `synthesis` 里预留接口 | `judgment/` 模块 8 个文件全部实装 |
| 定期报告 | 只是 `holdings` 的来源标签 | `periodic_report_reader` 按报告类型读全文、原文摘录、三类对照 |

### 新增能力

| 能力 | 层 | 作用 |
|---|---|---|
| `periodic_report_reader` | fact | 季报 / 中期报告 / 年报分类型阅读，财务报表、审计意见、重大事项、条款一致性、叙事对照 |
| `devils_advocate` | judgment | 五类反证找最薄弱假设，输出 `confidence_cap`，是 `synthesis` 的强制前置 |

### 行为变化（对老用户）

- 所有需要判断力的工作流现在多一步 `devils_advocate`；**`synthesis` 的反证段不再允许自行编写**，必须引用反证引擎输出
- 一票否决项从 `synthesis` 内嵌表格移到 `judgment/veto-rules.yaml`，阈值可由工作流 `defaults` 覆盖
- 结论强度受 `confidence_cap` 约束：`weak` / `invalid` 时禁止输出星级与适配度分档
- `lens` 定义移到 `judgment/lenses.yaml`，新增视角不改能力单元
- 决策日志默认不落盘；仅在用户显式授权下本地持久化，不上传、不入库、不进仓库
- 研报与报告全文运行时读取、读而不存，不打包再分发

### 升级步骤

1. 覆盖 `core/`、`capabilities/`、`contracts/`、`templates/`、`data/semantic-fields.yaml`、`policies/`（未改动）
2. 新增 `judgment/` 与 `workflows/judgment/`，新增 5 条工作流文件
3. 更新 `README.md`、`AGENTS.md` 触发词
4. 已有的 18 条工作流 YAML **无需改动**即可继续运行；判断层能力按需加入 DAG
5. 数据源配置、MCP 登录、`mcp.json` 全部不变

### 兼容性承诺

- 单一 Core 入口不变，平台薄适配不变
- DataGateway 与语义字段只增不改，旧字段口径不变
- 合规闸与固定免责声明不变
- 回退到 v2.0 只需移除 `judgment/` 与新增工作流，并将 `core/SKILL.md` 版本号回退

---

## 9. 验证阶段修复（结构验证，非端到端实跑）

确认当前会话**无已授权金融 MCP**后，执行 `python tools/validate.py` 做全量结构验证，发现并修复 4 类缺陷：

| # | 缺陷 | 修复 |
|---|---|---|
| 1 | 8 处模板占位符引用了契约里不存在的字段或块 | 契约补 `fund_basic` / `window` / `rating_dimensions` / `fund_universe` / `records`，`envelope` 补 `alert_summary`，`alert_report.md` 改用 `envelope.alert_summary.*` |
| 2 | `trading_costs` 无任何 provider 声明覆盖 | 在语义字段字典标 `source_type: assumption-driven`；`cost_model` 与 `gateway.md` 明确"用 `assumptions` 默认参数、标 `estimated`、列 `missing_fields`"，不硬塞 provider |
| 3 | `core/d_monitor`、`lifecycle/periodic_review`、`events/alert_reassessment` 三条 `include` 链路展开后出现 **2 个 synthesis** | `core/orchestrator.md` 第 10 条「include 的 synthesis 抑制」：子工作流的 `synthesis`/`render` 自动跳过，事实块仍进入 `$steps`，由最外层唯一 synthesis 收口 |
| 4 | `policies/compliance.md` 含两个代码块，机器容易取错代码块导致禁止词漏检 | 禁止词抽成 `policies/forbidden-words.txt` 单一事实源（27 词）；越界样例命中 6 词被拦截、合规样例无误杀 |

新增 `tools/validate.py`（7 组检查、可复跑、CI 友好）。当前 **0 错误 0 警告**；负向测试注入 3 个缺陷全部被抓到并退出码 1。

**随后已完成**：接真实 MCP 的端到端实跑（见第 10 节）。Skill 本身不代登录、不持密钥，授权由宿主客户端完成。

---

## 10. 真实 MCP 首跑与回填（v2.0-r1，2026-11-07）

宿主连接器 `wind-finance`（Wind Alice 万得金融数据）完成授权，按 `events/periodic_report_deep_read` 跑通完整链路。产物在 `runs/2026-11-07/`，均为一次性运行记录，**不参与路由、不写回静态映射**。

| # | 首跑发现 | 变更 |
|---|---|---|
| 1 | 公告检索可取基金季报/招募说明书片段，但**无法按章节定位全文** | `contracts/famas.contract.json` 的 `periodic_report` 块新增 `not_retrievable_sections`；`templates/periodic_report_memo.md` 增一行；`capabilities/periodic_report_reader.md` 区分 `not_retrievable` / `not_disclosed`，并要求相关对照标"无法对照"；`data/semantic-fields.yaml` 补 `retrieval_granularity` |
| 2 | 同一连接器的公告原文是 L1、结构化接口是 L2，原按 provider 整体等级选源会误过滤 L1 字段 | `data/gateway.md` 第三节新增「混合可信度 provider」；新增 `data/providers/wind-alice.yaml`（`trust_by_source_type`） |
| 3 | 单位错标、口径不明的派生指标、无窗口/无分母数值、分母不可比、复合基准被单指数替代、休市日快照状态 | `data/gateway.md` 第四节新增「实测口径陷阱」7 条规则 |
| 4 | 首启自检需要一个已验证样例 | `SETUP.md` 新增 5.1 节；`README.md` 验证章节与版本路线更新 |

**兼容性**：以上全部为**新增字段与新增规则**，未改动既有工作流、能力 ID、契约已有字段、模板已有占位符、合规条款与固定免责声明。回退到 v2.0 只需删除 `data/providers/wind-alice.yaml` 与 `runs/`，并撤销 `not_retrievable_sections` 契约字段与模板行；其余规则为纯文档说明，保留不影响运行。

**结论强度**：本轮 `confidence_cap = weak`，按 `judgment/framework.md` 未输出星级或适配度分档。这不是失败，而是判断层在真实数据上按预期生效：关键字段缺失与口径分歧被显式列出，而非被包装成看似完整的结论。

---

## 11. 补测与规则可执行化（v2.0-r2，2026-11-07 同日第二轮）

用户要求「能改的都改完」。本轮补测 5 类能力并更正首跑的一处判断偏差，再把文档规则落成机器可检查的约束。

### 11.1 补测结论（字段覆盖 9/12/14/3 → **10/12/13/3**）

| 补测 | 结果 |
|---|---|
| 场外净值序列 | 2026-10-08→2026-11-06 共 22 个交易日，单位/累计/复权净值三者相等；`fund_nav_history`、`fund_nav` 转 OK |
| 全市场筛选 | 组合条件返回 5 只，`fund_universe` 转 OK；目标基金规模 189.3266 亿元与持有人接口一致 |
| 管理人公司 | 在管 2.8403 万亿元、非货币 1.9981 万亿元、旗下 557 只；「基金经理 75752 个」判 `implausible_value` |
| 宏观 EDB | CPI（M0000612）可提数，10 年国债（S0059749）`code 1008` 指标级无权限 → `macro_rates` 转 PARTIAL |
| 财经新闻 | 返回券商研报摘录 → `research_reports` / `policy_text` 转 PARTIAL（L3 二手，仅作 `opinion_ref`） |

首版手工统计 9/12/14/3 **有误**（实际 7/10/18/3），现已由 `validate.py` 第 8 组自动解析覆盖表核对，杜绝再次漂移。

### 11.2 最重要的更正：不是"章节不可达"，是"跨文档误召回"

以完整章节标题检索可命中 §4.4 原文，但 5 条结果里 4 条是**其他基金**（招商蓝筹精选、易方达新常态、易方达产业优选、泰信蓝筹精选），含「总仓位 90%、港股 36%、A 类增长 26.24%」；目标基金只命中 §3.2。本基金 YTD 实为 **-24.7006%**，不校验标题就会得到方向相反、且看似有出处的结论。

| 新增约束 | 落点 |
|---|---|
| `document_title_match` 硬校验（主体/报告类型/报告期/披露日期） | `capabilities/periodic_report_reader.md`、`data/gateway.md`、`core/SKILL.md` Step 5 |
| `rejected_cross_document` 整条丢弃 | 同上 |
| `cross_document_recall` 否决项 → 结论 `invalid` | `judgment/veto-rules.yaml`、`judgment/framework.md` |
| 六类反证（新增⑥来源身份） | `capabilities/devils_advocate.md` |

### 11.3 另外三类新规则

- **基准版本化**：2026 年存量基金基准分批调整超 4000 只；实测同管理人旗下产品 2026-06-01 / 2026-07-27 生效新基准。`benchmark` 加 `versioning`，新增 `benchmark_version_change` 否决项与 `performance_metrics.md` 核对步骤；本轮 005827.OF 未取得变更公告全文，标 `benchmark_version_unverified` 并保持 `weak`。
- **指标级权限与二手研报**：`policies/source-trust.md` 新增降级分支；新闻中的研报摘录按 L3 + `second_hand` + 需核实原文，只作 `opinion_ref`。
- **单源降级**：`data-quality/cross_source_verify` 在只有 1 个数据源时改做同源内部一致性校验（带窗口 vs 无窗口、结构化 vs 一手文档、明细 vs 派生汇总），分歧标 `same_source_conflict`，不得冒充多源交叉验证通过。

### 11.4 两个可执行检查器

| 检查器 | 职责 |
|---|---|
| `tools/validate.py`（扩到 **8 组**） | 新增：工作流版本与 Core 一致、provider `coverage`/`known_gaps` 不冲突、`trust_by_source_type` 等级合法、规则锚点齐备、输出闸语法、`field_probe.md` 覆盖表统计自洽且总数等于语义字段数 |
| `tools/check_report.py`（新增） | 输出闸：禁止词（**合规元描述豁免**，修复自误伤根因）、固定免责声明逐字、溯源等级与时点、数据缺口与分歧、文档身份校验标记、基准版本核对、`estimated` 标注、`weak` 下不得出星级；内置自检 + `--strict` |

顺带把 **24 条工作流版本统一到 2.0.0**（原 17 条仍标 2.0.0）。

**兼容性**：仍为只增不改——新增契约字段 1 个（`not_retrievable_sections`）、否决项 2 个、能力规则若干、provider 1 个、检查器 1 个；既有工作流 DAG、能力 ID、模板占位符、合规条款与固定免责声明均未改动。`core/SKILL.md` 保持 2.0.0，r1/r2 视为兼容性修订。

**验证**：`validate.py` 常规与 `--strict` 均 0 错误 0 警告；`check_report.py` 对 3 份首跑产物 0 错误 0 警告。负向测试注入 5 个缺陷，`validate.py` 报 4 条 ERROR、`check_report.py` 命中 4 个禁止词，均退出码 1；另单独验证 provider 声明冲突规则可精确命中。v1 目录全程未改动。

