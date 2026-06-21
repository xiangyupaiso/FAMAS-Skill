![FAMAS 横幅](assets/banner.svg)

# FAMAS — 基金智选分析系统 🚀

![TRAE](https://img.shields.io/badge/TRAE-%20-blue) ![Claude%20Code](https://img.shields.io/badge/Claude%20Code-%20-purple) ![Codex](https://img.shields.io/badge/Codex-%20-orange) ![Skill](https://img.shields.io/badge/Skill-%20-green)

> **Fund Analysis Multi-Agent System**
>
>
> **首个** 基于多Agent协作的基金深度分析、筛选与持续监控决策支持系统 🧠

---

## 目录 (TOC)

- [项目简介](#项目简介)
- [系统架构](#系统架构-🏗️)
- [Agent 列表](#agent-列表-👥)
- [Agent 详细划分](#agent-详细划分-🔬)
- [工作流](#工作流)
- [快速开始](#快速开始-⚡)
- [项目结构](#项目结构-📁)
- [合规约束](#合规约束-⚠️)
- [迭代路线图](#迭代路线图-🛣️)
- [贡献指南](#贡献指南-🤝)
- [许可证](#许可证-📜)

---

## 项目简介 ✨

FAMAS 是一个面向个人投资者的基金分析决策支持系统，将基金分析任务拆解为 **10个专业化Agent**，覆盖 **"单基金深度分析 -> 多基金对比筛选 -> 组合持仓诊断 -> 持续监控"** 等完整流程。

### 核心设计原则 🧭

- **分工解耦**: 每个Agent只负责一个专业领域，避免单一Agent过载 ✅
- **数据驱动**: 所有结论必须基于可溯源的数据与计算 📊
- **合规前置**: 财富顾问Agent内置硬约束，禁止输出具体买卖信号 ⚖️
- **渐进可用**: 支持从极简单Agent到完整多Agent的渐进式部署 🛠️

---

## 系统架构 🏗️

```
(示意图略)
```

---

## Agent 列表 👥

| # | Agent | 职责 | 层级 |
|---|-------|------|------|
| 1 | `prospectus_analyzer` | 基金文档解析专员 🧾 | Layer 2 |
| 2 | `performance_analyst` | 业绩归因分析师 📈 | Layer 2 |
| 3 | `cost_analyzer` | 费率侦探 💰 | Layer 2 |
| 4 | `manager_profiler` | 基金经理画像师 👤 | Layer 2 |
| 5 | `macro_strategist` | 宏观策略顾问 🌍 | Layer 1 |
| 6 | `wealth_advisor` | 财富顾问（综合评级） 🏷️ | Layer 4 |
| 7 | `sector_screener` | 行业筛选引擎 🔎 | Layer 3 |
| 8 | `fund_comparator` | 多基金对比分析师 ⚖️ | Layer 3 |
| 9 | `portfolio_doctor` | 组合诊断师 🩺 | Layer 4 |
| 10 | `watchtower` | 监控预警塔 🚨 | Layer 0 |

---

## Agent 详细划分 🔬

<details>
<summary>展开 / 收起 Agent 详细信息</summary>

<!-- 下面保持原有详细内容：为了节省空间，这里仅摘录结构，完整文档仍在仓库中 -->

### Agent 1: prospectus_analyzer — 基金文档解析专员 🧾

- 职责: 穿透解析基金招募说明书、基金合同、托管协议、定期公告及持有人评价
- 核心输入: 招募书PDF / 证监会公告 / 季报 / 持有人结构数据
- 输出: 投资范围、业绩基准、可投资产类别、特殊限制条款、机构持有人比例、费率结构摘要

### Agent 2: performance_analyst — 业绩归因分析师 📈

- 职责: 对基金历史净值与持仓进行定量归因，解构收益来源与风险暴露
- 核心输出: 年化收益、最大回撤、夏普比率、行业偏离度、风格漂移系数等

### Agent 3: cost_analyzer — 费率侦探 💰

- 职责: 穿透显性费率与隐性成本，评估规模对策略的惩罚效应

### ...（其余 Agent 详见原文）

</details>

---

## 工作流 🛠️

系统预置 **4条核心工作流**：

- Workflow A: 单基金深度分析 🔍
- Workflow B: 行业/偏好筛选 🧾
- Workflow C: 组合持仓诊断 🧩
- Workflow D: 持续监控预警 ⏰

（详见下方工作流图）

---

## 快速开始 ⚡

### 1. 克隆仓库

```bash
git clone https://github.com/xiangyupaiso/FAMAS-Skill.git
cd FAMAS-Skill
```

### 2. 安装依赖

```bash
pip install akshare pandas numpy
```

### 演示图 / GIF

（可在此处添加演示截图或 GIF，建议放 assets/demo.gif）

---

## 项目结构 📁

（保���原有结构）

---

## 合规约束 ⚠️

- **禁止明确交易信号**: 严禁输出"买入"/"卖出"/"加仓"/"减仓"/"清仓"等指令 ❗
- **风险提示前置**: 所有评级输出必须附带核心风险提示 🛡️
- **适配度而非推荐度**: 输出框架为"该基金对XX类型投资者的适配度" 🧭

---

## 迭代路线图 🛣️

（保留原有路线图）

---

## 贡献指南 🤝

欢迎提交 Issue 和 PR！

---

## 许可证 📜

[MIT](LICENSE)

> **文档版本**: v2.1
> **最后更新**: 2026-06-21
> **维护者**: Fund Analysis Multi-Agent System Team
