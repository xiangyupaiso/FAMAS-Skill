---
name: "famas"
description: "FAMAS 基金分析系统唯一入口。分析基金、基金评级、筛选基金、对比基金、诊断持仓、组合再平衡、基金监控预警、定投适配、换基金评估、份额选择、季报解读、多源数据校验时统一使用本技能。"
argument-hint: "[自然语言描述你的基金分析需求]"
---

# FAMAS — Claude Code 平台适配层

本文件**只做平台接入**，不含任何分析流程、能力定义或合规条款。原 v1 的四条斜杠命令已合并为本单一入口，由 Core 按意图自动路由。

## 执行指令

1. 读取仓库根目录下的 `core/SKILL.md`（相对于本文件为 `../../../core/SKILL.md`）。
2. 严格按 `core/SKILL.md` 的「加载顺序」与「执行协议」执行。
3. 意图判定读 `core/router.md`；工作流从 `workflows/` 读取；能力定义从 `capabilities/` 读取。
4. 交付前必须按 `policies/compliance.md` 完成输出前检查。

## 原命令对照

| v1 命令 | v2 用法 |
|---|---|
| `/famas-analyze-fund 020712` | `/famas 分析基金 020712` |
| `/famas-screen-fund 科技成长` | `/famas 筛选科技成长基金` |
| `/famas-diagnose-portfolio 020712(30%)` | `/famas 诊断持仓 020712 30% ...` |
| `/famas-monitor-fund 020712` | `/famas 监控 020712` |

## 约束

- 不得在本文件复制、改写或缓存 core 的流程
- 不得绕过 core 直接调用 `capabilities/`
- 不得在本文件放置数据源配置或密钥

> MCP 登录引导见 `SETUP.md`；v1 完整迁移说明见 `MIGRATION.md`。
