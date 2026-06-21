# FAMAS — 基金智选分析系统

> **Fund Analysis Multi-Agent System**
>
>
> **首个**基于多Agent协作的基金深度分析、筛选与持续监控决策支持系统

---

## 项目简介

FAMAS 是一个面向个人投资者的基金分析决策支持系统，将基金分析任务拆解为 **10个专业化Agent**，覆盖 **"单基金深度分析 -> 多基金对比筛选 -> 组合持仓诊断 -> 持续监控预警"** 四个层级。

### 核心设计原则

- **分工解耦**: 每个Agent只负责一个专业领域，避免单一Agent过载
- **数据驱动**: 所有结论必须基于可溯源的数据与计算
- **合规前置**: 财富顾问Agent内置硬约束，禁止输出具体买卖信号
- **渐进可用**: 支持从极简单Agent到完整多Agent的渐进式部署

---

## 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Layer 4: 决策输出层                           │
│  ├─ wealth_advisor      -> 综合评级(1-5星) + 时机矩阵 + 适配投资者类型   │
│  └─ portfolio_doctor    -> 现有持仓再平衡与风险诊断                     │
├─────────────────────────────────────────────────────────────────────┤
│                        Layer 3: 对比筛选层                           │
│  ├─ sector_screener     -> 按行业/主题/风格偏好筛选候选标的             │
│  └─ fund_comparator     -> 多基金横向PK与淘汰建议                      │
├─────────────────────────────────────────────────────────────────────┤
│                        Layer 2: 单基金深度层                         │
│  ├─ prospectus_analyzer -> 招募书、合同、公告、持有人结构解析           │
│  ├─ performance_analyst -> 净值归因、回撤控制、风格漂移监测             │
│  ├─ cost_analyzer       -> 显性费率 + 隐性成本 + 规模惩罚穿透           │
│  └─ manager_profiler    -> 基金经理画像、稳定性、逆风表现               │
├─────────────────────────────────────────────────────────────────────┤
│                        Layer 1: 宏观环境层                           │
│  └─ macro_strategist    -> 利率/汇率/政策/市场风格适配度               │
├─────────────────────────────────────────────────────────────────────┤
│                        Layer 0: 监控预警层                           │
│  └─ watchtower          -> 经理变更/规模异动/风格漂移/业绩掉队预警       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Agent 列表

| # | Agent | 职责 | 层级 |
|---|-------|------|------|
| 1 | `prospectus_analyzer` | 基金文档解析专员 | Layer 2 |
| 2 | `performance_analyst` | 业绩归因分析师 | Layer 2 |
| 3 | `cost_analyzer` | 费率侦探 | Layer 2 |
| 4 | `manager_profiler` | 基金经理画像师 | Layer 2 |
| 5 | `macro_strategist` | 宏观策略顾问 | Layer 1 |
| 6 | `wealth_advisor` | 财富顾问（综合评级） | Layer 4 |
| 7 | `sector_screener` | 行业筛选引擎 | Layer 3 |
| 8 | `fund_comparator` | 多基金对比分析师 | Layer 3 |
| 9 | `portfolio_doctor` | 组合诊断师 | Layer 4 |
| 10 | `watchtower` | 监控预警塔 | Layer 0 |

---
## Agent 详细划分

### Agent 1: prospectus_analyzer — 基金文档解析专员

| 项目               | 说明                                                                         |
| ------------------ | ---------------------------------------------------------------------------- |
| **职责**     | 穿透解析基金招募说明书、基金合同、托管协议、定期公告及持有人评价             |
| **核心输入** | 基金代码 -> 招募书PDF / 证监会公告 / 季报 / 持有人结构数据                   |
| **核心输出** | 投资范围、业绩基准、可投资产类别、特殊限制条款、机构持有人比例、费率结构摘要 |
| **关键指标** | 股票仓位上下限、港股通权限、衍生品权限、大额赎回条款、机构/个人持有占比      |
| **工具依赖** | `fund_prospectus`, `fund_announcement`, `fund_holder_structure`        |
| **输出格式** | 结构化JSON + 关键条款风险摘要                                                |

---

### Agent 2: performance_analyst — 业绩归因分析师

| 项目               | 说明                                                                         |
| ------------------ | ---------------------------------------------------------------------------- |
| **职责**     | 对基金历史净值与持仓进行定量归因，解构收益来源与风险暴露                     |
| **核心输入** | 基金代码 -> 历史净值序列、历史季报/半年报持仓明细、基准指数数据              |
| **核心输出** | 年化收益、最大回撤、夏普比率、卡玛比率、行业偏离度、风格漂移系数、换手率趋势 |
| **关键指标** | 相对基准超额收益(alpha)、回撤修复天数、季度风格漂移距离、行业集中度(HHI)     |
| **工具依赖** | `fund_nav_history`, `fund_holding_history`, `benchmark_index`          |
| **输出格式** | 风险收益画像表 + 风格漂移趋势图 + 行业轮动热力图                             |

---

### Agent 3: cost_analyzer — 费率侦探

| 项目               | 说明                                                                                       |
| ------------------ | ------------------------------------------------------------------------------------------ |
| **职责**     | 穿透显性费率与隐性成本，评估规模对策略的惩罚效应                                           |
| **核心输入** | 基金代码 -> 费率结构、历史换手率、规模变化曲线、申赎记录                                   |
| **核心输出** | 总持有成本(TCR)、隐性交易成本估算、规模惩罚评估、QDII附加费分析                            |
| **关键指标** | 管理费率+托管费率+销售服务费率、换手率隐含成本率、清盘风险阈值(<2亿)、策略钝化阈值(>100亿) |
| **工具依赖** | `fund_fee_structure`, `fund_turnover`, `fund_scale_history`                          |
| **输出格式** | 成本侵蚀模拟表 + 规模友好度评级                                                            |

---

### Agent 4: manager_profiler — 基金经理画像师

| 项目               | 说明                                                                  |
| ------------------ | --------------------------------------------------------------------- |
| **职责**     | 对主动管理型基金的核心——基金经理进行立体画像                        |
| **核心输入** | 基金经理姓名 -> 历史管理产品列表、各产品任职区间、季报重仓特征        |
| **核心输出** | 能力圈图谱、稳定性评分、逆风年份相对排名、风格漂移历史、共管/跳槽记录 |
| **关键指标** | 单只基金任职年限、能力圈行业数、左侧/右侧交易特征、跳槽频率、共管比例 |
| **工具依赖** | `manager_history`, `manager_fund_list`, `manager_style_trace`   |
| **输出格式** | 经理画像卡 + 稳定性雷达图                                             |

---

### Agent 5: macro_strategist — 宏观策略顾问

| 项目               | 说明                                                                           |
| ------------------ | ------------------------------------------------------------------------------ |
| **职责**     | 评估基金策略与当前宏观环境的匹配度，提供风格轮动背景                           |
| **核心输入** | 当前利率曲线、汇率走势、市场风格指数(大盘/小盘/价值/成长)、政策文本            |
| **核心输出** | 宏观适配度评分、当前市场风格定位、对基金策略的顺风/逆风判断                    |
| **关键指标** | 10年期国债收益率分位、人民币汇率波动率、风格轮动强度、产业政策热度             |
| **工具依赖** | `macro_interest_rate`, `macro_fx`, `market_style_index`, `policy_text` |
| **输出格式** | 宏观环境适配度评分(0-100) + 风格轮动建议                                       |

---

### Agent 6: wealth_advisor — 财富顾问（综合评级与时机判断）

| 项目                   | 说明                                                                                                                                |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **职责**         | 整合前序所有Agent输出，结合宏观环境给出综合评级与时机判断                                                                           |
| **核心输入**     | `prospectus_analyzer`输出、`performance_analyst`输出、`macro_strategist`输出、`cost_analyzer`输出、`manager_profiler`输出 |
| **核心输出**     | **晨星式星级评定(1-5星)**、**时机矩阵**、适配投资者类型、风险提示                                                       |
| **关键约束**     | **严禁输出"买入"/"卖出"/"加仓"/"减仓"等明确交易信号**                                                                         |
| **时机矩阵示例** | "当前估值分位处于近5年30%位置，对长期配置型资金具备吸引力，对趋势交易型资金需等待右侧确认"                                          |
| **输出格式**     | 综合评级卡 + 时机矩阵 + 适配投资者画像 + 核心风险提示                                                                               |

---

### Agent 7: sector_screener — 行业筛选引擎

| 项目               | 说明                                                                |
| ------------------ | ------------------------------------------------------------------- |
| **职责**     | 根据用户给定的行业、主题或风格偏好，从全市场基金池中筛选匹配标的    |
| **核心输入** | 用户偏好(行业/主题/风格/资产类别) + 全市场基金池                    |
| **核心输出** | 候选基金池(Top 10-20)、筛选逻辑说明、ETF联接映射关系、伪分散预警    |
| **筛选逻辑** | 持仓行业穿透、ETF联接映射、风格标签匹配、QDII特殊处理、债券久期匹配 |
| **关键指标** | 目标行业持仓占比、风格纯度、场内ETF与场外联接基金映射、重合度阈值   |
| **工具依赖** | `fund_pool_query`, `sector_classification`, `etf_linkage_map` |
| **输出格式** | 筛选结果表 + 每只基金的匹配度评分 + 逻辑说明                        |

---

### Agent 8: fund_comparator — 多基金对比分析师

| 项目               | 说明                                                                |
| ------------------ | ------------------------------------------------------------------- |
| **职责**     | 对用户指定的2-5只候选基金进行横向PK，输出淘汰建议与组合优化方向     |
| **核心输入** | 2-5只基金代码 -> 各Agent单基金分析结果                              |
| **核心输出** | 雷达图对比数据、持仓重合度、费率侵蚀模拟、经理稳定性对比、淘汰建议  |
| **关键指标** | 同等回撤下收益排名、前十大重仓股重叠率、3年费率侵蚀差、策略容量余量 |
| **输出格式** | 对比矩阵表 + 雷达图数据 + 淘汰/保留建议                             |

---

### Agent 9: portfolio_doctor — 组合诊断师

| 项目               | 说明                                                         |
| ------------------ | ------------------------------------------------------------ |
| **职责**     | 对用户当前持有的多只基金进行组合级风险诊断与再平衡建议       |
| **核心输入** | 用户持仓列表(基金代码+持有比例)                              |
| **核心输出** | 行业集中度、风格偏离度、资产类别缺口、隐性相关性、再平衡建议 |
| **关键指标** | 前三大行业占比、股债配比、不同基金间重仓股重合度、风格偏离度 |
| **输出格式** | 组合风险画像 + 集中度热力图 + 再平衡方案                     |

---

### Agent 10: watchtower — 监控预警塔

| 项目               | 说明                                                                                                          |
| ------------------ | ------------------------------------------------------------------------------------------------------------- |
| **职责**     | 对用户关注/持有的基金进行持续监控，触发异动预警                                                               |
| **核心输入** | 监控基金列表 + 预警规则配置                                                                                   |
| **核心输出** | 异动预警通知(经理变更、规模异动、风格漂移、业绩掉队、费率调整、公告风险)                                      |
| **触发条件** | 经理离职/新增共管、单季度规模+-30%、风格偏离历史中枢1个标准差、连续两季度跑输基准5%、管理费调整、大额赎回公告 |
| **工具依赖** | `fund_news_monitor`, `fund_scale_alert`, `fund_style_alert`                                             |
| **输出格式** | 预警列表(优先级排序) + 异动详情 + 建议关注事项                                                                |

---

## 工作流

系统预置 **4条核心工作流**：

### Workflow A: 单基金深度分析
```
用户输入: 基金代码
    |
    v
+----------------------+
| prospectus_analyzer  | --> 解析文档结构
+-----------+----------+
            |
+-----------+-----------+
| performance_analyst  | --> 业绩归因与风险解构
| cost_analyzer        | --> 费率与成本穿透
| manager_profiler     | --> 经理画像(如为主动管理型)
+-----------+----------+
            |
+-----------+-----------+
| macro_strategist     | --> 宏观环境适配度
+-----------+----------+
            |
+-----------v-----------+
| wealth_advisor       | --> 综合评级 + 时机矩阵 + 风险提示
+-----------------------+
```

### Workflow B: 行业/偏好筛选
```
用户输入: 行业/主题/风格偏好
    |
    v
+----------------------+
| sector_screener      | --> 全市场初筛(Top 50)
+-----------+----------+
            |
+-----------v-----------+
| fund_comparator      | --> 对Top 10进行横向PK
+-----------------------+
```

### Workflow C: 组合持仓诊断
```
用户输入: 持仓列表(基金代码+比例)
    |
    v
+----------------------+
| portfolio_doctor     | --> 组合级风险扫描
+-----------+----------+
            |
+-----------v-----------+
| cost_analyzer        | --> 组合总持有成本计算
| fund_comparator      | --> 持仓基金间重合度分析
+-----------------------+
```

### Workflow D: 持续监控预警
```
用户输入: 监控基金列表 + 预警阈值配置
    |
    v
+----------------------+
| watchtower           | --> 定期巡检(每日/每周)
|   |- 经理变更监控     |
|   |- 规模异动监控     |
|   |- 风格漂移监控     |
|   |- 业绩掉队监控     |
|   |- 费率调整监控     |
|   |- 公告风险监控     |
+----------------------+
```

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/xiangyupaiso/FAMAS-Skill.git
cd FAMAS-Skill
```

### 2. 安装依赖

```bash
pip install akshare pandas numpy
```

### 3. 在 TRAE 中使用

将 `.trae/skills/famas-fund-analysis/` 目录复制到你的 TRAE 工作区的 `.trae/skills/` 目录下：

```bash
cp -r .trae/skills/famas-fund-analysis /path/to/your/workspace/.trae/skills/
```

### 4. 在 Claude Code 中使用

将 `.claude/skills/` 目录复制到你的项目根目录下：

```bash
cp -r .claude/skills /path/to/your/project/.claude/skills
```

### 5. 在 OpenAI Codex CLI 中使用

将 `.agents/skills/` 目录和 `AGENTS.md` 复制到你的项目根目录下：

```bash
cp -r .agents/skills /path/to/your/project/.agents/skills
cp AGENTS.md /path/to/your/project/AGENTS.md
```

Codex 会自动识别 `.agents/skills/` 中的 Skills，根据 `description` 中的触发词自动加载。

### 6. 命令速查

| 平台 | 命令 | 用途 | 示例 |
|------|------|------|------|
| Claude Code | `/famas-analyze-fund` | 单基金深度分析 | `/famas-analyze-fund 020712` |
| Claude Code | `/famas-screen-fund` | 行业/偏好筛选 | `/famas-screen-fund 科技成长` |
| Claude Code | `/famas-diagnose-portfolio` | 组合持仓诊断 | `/famas-diagnose-portfolio 020712(30%), 005911(25%)` |
| Claude Code | `/famas-monitor-fund` | 持续监控预警 | `/famas-monitor-fund 020712, 005911` |
| Codex | `famas-analyze-fund` | 单基金深度分析 | 自动触发或手动调用 |
| Codex | `famas-screen-fund` | 行业/偏好筛选 | 自动触发或手动调用 |
| Codex | `famas-diagnose-portfolio` | 组合持仓诊断 | 自动触发或手动调用 |
| Codex | `famas-monitor-fund` | 持续监控预警 | 自动触发或手动调用 |

Claude Code 和 Codex 都会根据对话内容自动触发对应的 Skill，无需手动输入命令。

---

## 项目结构

```
FAMAS-Skill/
├── AGENTS.md                     # Codex 项目级指令文件
├── .trae/
│   └── skills/
│       └── famas-fund-analysis/
│           └── SKILL.md          # TRAE Skill 主文档
├── .claude/
│   └── skills/
│       ├── famas-analyze-fund/
│       │   └── SKILL.md          # Claude Code: /famas-analyze-fund
│       ├── famas-screen-fund/
│       │   └── SKILL.md          # Claude Code: /famas-screen-fund
│       ├── famas-diagnose-portfolio/
│       │   └── SKILL.md          # Claude Code: /famas-diagnose-portfolio
│       └── famas-monitor-fund/
│           └── SKILL.md          # Claude Code: /famas-monitor-fund
├── .agents/
│   └── skills/
│       ├── famas-analyze-fund/
│       │   └── SKILL.md          # Codex: 单基金深度分析
│       ├── famas-screen-fund/
│       │   └── SKILL.md          # Codex: 行业/偏好筛选
│       ├── famas-diagnose-portfolio/
│       │   └── SKILL.md          # Codex: 组合持仓诊断
│       └── famas-monitor-fund/
│           └── SKILL.md          # Codex: 持续监控预警
├── agents/                       # 各Agent的System Prompt
│   ├── prospectus_analyzer.md
│   ├── performance_analyst.md
│   ├── cost_analyzer.md
│   ├── manager_profiler.md
│   ├── macro_strategist.md
│   ├── wealth_advisor.md
│   ├── sector_screener.md
│   ├── fund_comparator.md
│   ├── portfolio_doctor.md
│   └── watchtower.md
├── workflows/                    # 工作流定义
│   ├── workflow_a_single_fund.md
│   ├── workflow_b_sector_screen.md
│   ├── workflow_c_portfolio.md
│   └── workflow_d_monitoring.md
├── templates/                    # 输出模板
│   ├── comprehensive_rating_card.md
│   ├── sector_screening_report.md
│   ├── portfolio_diagnosis_report.md
│   └── monitoring_alert_report.md
└── README.md
```

---

## 合规约束

### 硬约束（不可突破）

- **禁止明确交易信号**: 严禁输出"买入"/"卖出"/"加仓"/"减仓"/"清仓"等指令
- **风险提示前置**: 所有评级输出必须附带核心风险提示
- **适配度而非推荐度**: 输出框架为"该基金对XX类型投资者的适配度"
- **历史业绩不预示未来**: 必须包含标准免责声明
- **分层agent保证输出准确性**：除layer4之外的agent只能输出整理的事实，不能输出任何自己的观点，避免影响上层和报告的客观性和准确性

---

## 迭代路线图

| 版本 | 目标 | 新增Agent/功能 |
|------|------|----------------|
| **v1.0** | 单基金深度分析可用 | prospectus_analyzer + performance_analyst + wealth_advisor |
| **v1.1** | 筛选能力上线 | sector_screener + fund_comparator |
| **v1.2** | 组合诊断上线 | portfolio_doctor + cost_analyzer |
| **v1.3** | 经理画像完善 | manager_profiler |
| **v1.4** | 宏观适配上线 | macro_strategist |
| **v2.0** | 持续监控上线 | watchtower，支持定时巡检与预警推送 |
| **v2.1** | 增强底座客观性 | 添加硬约束，底层agent必须只能输出事实 |

---

## 贡献指南

欢迎提交 Issue 和 PR！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

---

## 许可证

[MIT](LICENSE)

---

> **文档版本**: v2.1
> **最后更新**: 2026-06-21
> **维护者**: Fund Analysis Multi-Agent System Team
