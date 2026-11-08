---
name: "famas"
description: "FAMAS 基金分析系统唯一入口。分析基金、基金评级、筛选基金、对比基金、诊断持仓、组合再平衡、基金监控预警、定投适配、换基金评估、份额选择、季报解读、多源数据校验时统一使用本技能。"
---

# FAMAS — TRAE 平台适配层

本文件**只做平台接入**，不含任何分析流程、能力定义或合规条款。

## 执行指令

1. 读取仓库根目录下的 `core/SKILL.md`（相对于本文件为 `../../../core/SKILL.md`）。
2. 严格按 `core/SKILL.md` 的「加载顺序」与「执行协议」执行。
3. 意图判定读 `core/router.md`，命中的工作流从 `workflows/` 读取，能力定义从 `capabilities/` 读取。
4. 交付前必须按 `policies/compliance.md` 完成输出前检查。

## 约束

- 不得在本文件复制、改写或缓存 core 的流程
- 不得绕过 core 直接调用 `capabilities/`
- 不得在本文件放置数据源配置或密钥

> 完整文档见仓库根 `README.md`；MCP 登录引导见 `SETUP.md`。
