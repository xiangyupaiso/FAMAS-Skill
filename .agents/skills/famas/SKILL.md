---
name: "famas"
description: "FAMAS 基金分析系统唯一入口。触发词：分析基金、基金评级、筛选基金、找基金、基金对比、诊断持仓、组合诊断、再平衡、监控基金、基金预警、异动提醒、定投适配、换基金、A类C类、季报解读、多源校验。"
---

# FAMAS — Codex CLI 平台适配层

本文件**只做平台接入**，不含任何分析流程、能力定义或合规条款。原 v1 的四个 skill 已合并为本单一入口。

## 执行指令

1. 读取仓库根目录下的 `core/SKILL.md`（相对于本文件为 `../../../core/SKILL.md`）。
2. 严格按 `core/SKILL.md` 的「加载顺序」与「执行协议」执行。
3. 意图判定读 `core/router.md`；工作流从 `workflows/` 读取；能力定义从 `capabilities/` 读取。
4. 交付前必须按 `policies/compliance.md` 完成输出前检查。

## 约束

- 不得在本文件复制、改写或缓存 core 的流程
- 不得绕过 core 直接调用 `capabilities/`
- 不得在本文件放置数据源配置或密钥
- 项目级 `AGENTS.md` 只声明触发词与合规摘要，不作为逻辑源

> MCP 登录引导见 `SETUP.md`；v1 完整迁移说明见 `MIGRATION.md`。
