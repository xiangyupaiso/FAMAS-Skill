# FAMAS — 基金智选分析系统

> **Fund Analysis Multi-Agent System**
>
> 基于多Agent协作的基金深度分析、筛选与持续监控决策支持系统

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

## 工作流

系统预置 **4条核心工作流**：

### Workflow A: 单基金深度分析
```
prospectus_analyzer -> performance_analyst + cost_analyzer + manager_profiler
-> macro_strategist -> wealth_advisor
```

### Workflow B: 行业/偏好筛选
```
sector_screener -> fund_comparator
```

### Workflow C: 组合持仓诊断
```
portfolio_doctor -> cost_analyzer + fund_comparator
```

### Workflow D: 持续监控预警
```
watchtower (定期巡检)
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

> **文档版本**: v1.0
> **最后更新**: 2026-06-21
> **维护者**: Fund Analysis Multi-Agent System Team
