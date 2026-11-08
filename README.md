<div align="center">

# FAMAS

**Fund Analysis & Monitoring Agent System**

![release](https://img.shields.io/badge/release-v2.0-1c3d5e.svg)
![license](https://img.shields.io/badge/license-MIT-green.svg)
![workflows](https://img.shields.io/badge/workflows-24-2f6da8.svg)
![MCP](https://img.shields.io/badge/MCP-ready-blue.svg)
![validation](https://img.shields.io/badge/checks-0%20errors-brightgreen.svg)

**一个 Core · 24 条自由组合的工作流 · 登录一次数据源，之后自动调用**

[简体中文](README.md) · **[English](README.en.md)**

</div>

---

FAMAS 是一套**基金分析与监控的 Agent Skill**：把基金评估拆成单一 Core、声明式工作流、无 persona 的能力单元和一层可执行的合规闸。它不预测涨跌，只做三件事——**把数字取准、把假设讲清、把结论约束在证据允许的范围内**。

> 它不是投资建议工具。任何评级、适配度或风险描述都以「信息整理 + 可溯源事实」为边界。

---

## 为什么是 v2.0

v1 把同一份逻辑复制了 5 遍：9 个 skill 入口（Claude Code 4 + Codex 4 + TRAE 1）、10 个带人设的 Agent、4 条工作流在 5 处重复定义，约 1600+ 行描述同一件事。角色冗余、字段口径不一致，用户还得记住每个命令是干什么的。

v2.0 把它收敛成**一个逻辑源**：

| | v1 | v2.0 |
|---|---|---|
| 入口 | 9 个 skill + 10 个 Agent 人设 | **1 个 Core** + 3 份约 20 行平台适配 |
| 工作流定义 | 4 条，复制 5 处 | **24 条声明式 YAML**，支持 `include` / 覆盖 / 临时拼装 |
| 字段契约 | 费率、评级卡、合规格各写一遍 | `contracts/famas.contract.json` **唯一定义** |
| 数据 | 靠模型记忆与手工输入 | **MCP 数据层**：38 个语义字段 → 运行时 `tools/list` 探测 |
| 合规 | 散在 4 处，曾整章丢失 | `policies/compliance.md` 一处定义，**输出前强制执行** |
| 结论 | 直接给星级 | 反证引擎 + 四段式 + 一票否决 + 置信度上限 |

重复内容从 1600+ 行降到约 60 行。用户只需记住 `famas` 一个词。

---

## 架构

```mermaid
flowchart LR
    U["用户自然语言"] --> C["Core 意图路由"]
    C --> W["声明式工作流 YAML"]
    W --> R["能力注册表"]
    R --> G["DataGateway"]
    G --> M[("已授权的金融 MCP")]
    M --> F["事实块 + provenance"]
    F --> D["反证引擎"]
    D --> S["四段式综合层"]
    S --> P["合规闸 / 输出闸"]
    P --> O["带出处的报告"]

    style C fill:#1c3d5e,color:#fff
    style P fill:#b45309,color:#fff
    style M fill:#2f6da8,color:#fff
```

**分层原则**：事实层只出事实（9 个无 persona 能力 + 定期报告阅读），判断层只出反证，综合层是**唯一允许出观点**的地方。监控不再是 Agent，而是 `triggers/rules.yaml` 里的阈值规则 + 宿主调度器。

---

## 快速开始

### 1. 安装

把本仓库放到工作区即可。三个平台的薄适配已就绪，逻辑只有一份：

```
.trae/skills/famas/SKILL.md     .claude/skills/famas/SKILL.md     .agents/skills/famas/SKILL.md
```

### 2. 登录数据源（一次性）

> **登录的是数据源方的 MCP，不是 FAMAS。** FAMAS 是纯文本 Skill，没有账号、没有登录入口、也不持有密钥。授权（OAuth 2.1 + PKCE 或 API Key）由宿主客户端完成。

在宿主客户端连接任意一个金融数据源，首启自检说一句 **「检查一下数据源」** 即可。完整引导见 [SETUP.md](SETUP.md)，配置模板见 [mcp.json](mcp.json)。

- 登录 **1 个** MCP 就能跑通；字段未覆盖的部分会显式列进 `missing_fields`，**不会编数字**
- 多登几个可做交叉校验与可信度分级；一个都不登也能用，只输出分析框架与待补字段清单
- 令牌过期或额度用尽时，宿主会再弹一次授权——那是数据源侧的事，不是 Skill 失效

### 3. 直接用自然语言

```
分析一下 005827               →  core/a_single_fund
读一下这份季报                →  events/periodic_report_deep_read
这两只基金换哪只更合适        →  lifecycle/fund_replacement
上次那个预警，重新评估一下    →  events/alert_reassessment（自动 include 单基金深度）
检查一下数据源                →  data-quality/cross_source_verify（轻量自检）
```

全部意图映射见 [core/router.md](core/router.md)。

---

## 核心设计

| 设计 | 说明 | 落点 |
|---|---|---|
| **单一 Core** | `description` 只负责触发与路由；平台适配不含流程逻辑 | [core/SKILL.md](core/SKILL.md) |
| **声明式工作流** | 串行 / 并行 / 条件 / `include` / 降级 / 现场拼装，不生成新文件 | [workflows/\_schema.md](workflows/_schema.md) · [core/orchestrator.md](core/orchestrator.md) |
| **单一契约** | 字段只认一份 JSON；模板只渲染，合规只定义一次 | [contracts/famas.contract.json](contracts/famas.contract.json) |
| **语义字段层** | Core 不认厂商、不认工具名；38 个语义字段 → 运行时探测 | [data/gateway.md](data/gateway.md) · [data/semantic-fields.yaml](data/semantic-fields.yaml) |
| **可信度分级** | L1 一手披露 > L2 持牌数据商 > L3 二手 > L4 禁止；冲突列分歧，不静默取一个 | [policies/source-trust.md](policies/source-trust.md) |
| **合规闸** | 输出前扫描禁止词、风险前置、固定免责声明、逐字段溯源 | [policies/compliance.md](policies/compliance.md) |
| **判断层** | 六类反证 → 一票否决 → 四段式结论 → 置信度上限 | [judgment/README.md](judgment/README.md) |

### 数据层怎么打通

```mermaid
flowchart LR
    A["工作流声明 requires"] --> B["网关按 trust_min 选源"]
    B --> C["tools/list 运行时探测"]
    C --> D["语义字段 → 工具 临时映射"]
    D --> E["取数 + 口径归一"]
    E --> F["冲突检测 + provenance"]
    F --> G["事实块"]
```

映射表**只在会话内存活**，不写回仓库。换数据源只需加一个 `data/providers/<id>.yaml`，**不改任何工作流、能力、模板或合规文件**。已实测的连接器声明见 [data/providers/wind-alice.yaml](data/providers/wind-alice.yaml)。

---

## 24 条工作流

| 分类 | 数量 | 代表场景 |
|---|---:|---|
| `core` | 4 | 单基金深度、全市场筛选、组合诊断、监控告警 |
| `lifecycle` | 4 | 适配性检查、**换基金替换评估**、目标反推配置、定期复查 |
| `events` | 4 | 季报持仓变动、**定期报告深度阅读**、告警→重评估闭环、公司行动 / 经理变更影响 |
| `research` | 4 | A/C 份额与 ETF 联接成本临界点、伪分散穿透、运气还是能力、管理人集中度 |
| `data-quality` | 2 | 多源交叉校验、结论溯源审计 |
| `judgment` | 3 | 结论压力测试、季度校准、机构观点核对 |

另有 3 条深度研究场景覆盖**管理人叙事漂移**、**招募书条款一致性核对**与**跨期报告对照**。告警→重评估闭环把 v1 断掉的「只报警不复盘」链路接上了。

---

## 专业度是怎么做出来的

不是靠喂研报语料——Skill 是提示词不是权重，塞语料只会挤占上下文、立刻过期，还会把卖方研报的结论先行与乐观偏误一起学进来。专业度被工程化成四层：

1. **四段式判断**：核心假设 → 支持证据 → 反证 → 失效条件。缺第 3 或第 4 段，判为不合格输出、退回重做。
2. **反证引擎**：六类模式（口径 / 归因 / 时间 / 结构 / 替代解释 / 来源身份），输出 `confidence_cap` 限制结论强度。
3. **决策日志**：季度校准把误差归到数据 / 口径 / 框架三层；默认不落盘，需用户授权且仅本地。
4. **视角切换**：`fund_manager` / `FOF` / `risk` / `channel_advisor` 等 lens 换框架不改数字。

**越敢下结论，越依赖输出前那道闸**：`weak` / `invalid` 下禁止输出星级与适配度分档。

### 定期报告是被阅读的对象

季报 / 半年报 / 年报不只是 `holdings` 的来源标签。[capabilities/periodic_report_reader.md](capabilities/periodic_report_reader.md) 按报告类型区分必读章节（季报不推定存在审计意见），做三类对照——**说的 vs 做的、上期说的 vs 本期做的、合同 vs 实际**，并与 `fee_schedule` 交叉验证费用口径。管理人表述是**待检验的假设**，不是结论。

实测教训：文档检索会返回**其他基金**的同名章节。因此任何摘录前必须做 `document_title_match` 校验，标题不匹配整条标 `rejected_cross_document` 剔除，命中否决项时结论判 `invalid`。

---

## 验证状态

已在宿主授权 **Wind Alice 万得金融数据** 后完成真实端到端首跑（标的 005827.OF，报告期 2026Q3）：取数 → 反证 → 四段式 → 合规闸 → 渲染全链路打通。产物在 [首跑报告](runs/2026-11-07/first_run_report.md)，逐字段探测见 [field_probe.md](runs/2026-11-07/field_probe.md)。

首跑结论强度为 `weak`（目标文档章节未命中 + 跨文档误召回风险 + 基准版本未核对 + 多处口径冲突），**按框架未输出星级与适配度分档**——这是判断层按预期生效，不是链路失败。

```bash
python tools/validate.py            # 8 组结构检查
python tools/validate.py --strict   # 警告也视为失败
python tools/check_report.py        # 输出闸：runs/ 下每份报告交付前扫描
```

两个检查器常规与严格模式均 **0 错误 0 警告**（85 文件 / 24 工作流 / 11 能力 / 38 语义字段 / 13 契约块 / 7 模板 / 11 provider / 27 禁止词）。负向测试注入缺陷可稳定抓到并以退出码 1 失败。

**仍受外部条件限制**：目标基金定期报告 §4.4 章节全文、第二个已授权数据源（真多源交叉校验）、机构研报全文与关键假设表、决策日志落盘（需用户授权）。这些不会被估算值填补，只会显式降级并列入 `missing_fields`。

---

## 目录

```
FAMAS-Skill/
├── core/                    # 唯一逻辑源：SKILL / router / orchestrator / 能力注册表
├── capabilities/            # 9 事实层 + 1 判断层 + 1 综合层（无 persona）
├── judgment/                # 四段式框架 / 反证 / 决策日志 / 校准 / lens / 否决项
├── workflows/               # 24 条声明式 YAML（6 个分类）
├── contracts/               # 单一字段契约
├── templates/               # 7 个渲染模板
├── policies/                # 合规唯一定义 + 可信度分级 + 禁止词唯一事实源
├── triggers/                # 监控阈值规则（不是 Agent）
├── data/                    # gateway + 语义字段字典 + providers/（11 家）
├── tools/                   # validate.py（8 组）+ check_report.py（输出闸）
├── runs/                    # 一次性真实数据运行产物，不参与路由
├── .trae/.claude/.agents/   # 3 份平台薄适配，各约 20 行
├── SETUP.md                 # MCP 登录引导
├── mcp.json                 # 配置结构模板，全是 ${...} 占位符
├── MIGRATION.md             # v1 → v2.0 完整映射与回退说明
├── README.en.md             # English version
├── AGENTS.md / .gitignore / LICENSE
```

---

## 合规

唯一定义在 [policies/compliance.md](policies/compliance.md)，由 Core 在**输出前**强制执行：禁止交易信号、风险提示前置、适配度而非推荐度、固定免责声明、事实层不得夹带观点、每个数字可追溯到来源 + 时点 + 口径、数据缺口必须显式列出。报告类输出另须标注「报告期末快照，非实时」，且不得输出「违规 / 合规」等定性法律判断。

> 本报告仅作信息整理与适配度分析，不构成投资建议。基金过往业绩不预示未来表现。市场有风险，投资需谨慎。

---

## 兼容性与迁移

v2.0 对 v1 的 9 个入口提供完整命令映射与兼容层，见 [MIGRATION.md](MIGRATION.md)。发布版本为 **v2.0**；`r1 / r2` 为兼容性修订，只新增字段与规则，不改动既有工作流 DAG、能力 ID、模板占位符、合规条款与固定免责声明，可安全回退。

数据来源现状整理自 2026 年公开资料，**非实时核验**；接入地址、工具清单、额度与开通条件一律以厂商官方文档为准。监管机构与交易所目前未开放面向公众的官方 MCP，因此「权威」的准确表述是 **持牌数据商同源 + 每个数字可溯源**，不是监管官方直连。

[MIT](LICENSE) · 有问题或想加新工作流，欢迎提 Issue / PR。
