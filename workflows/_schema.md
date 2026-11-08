# 工作流 YAML 规范（DSL）

> 工作流只声明「做什么 + 按什么顺序 + 输出成什么」，**不含执行流程、能力定义、字段定义、合规条款**。这四类内容分别归 `core/orchestrator.md`、`capabilities/`、`contracts/`、`policies/`。

## 顶层字段

| 字段 | 必填 | 说明 |
|---|---|---|
| `id` | 是 | 与文件路径一致（如 `core/a_single_fund`），被 `core/router.md` 引用 |
| `version` | 是 | 工作流定义版本 |
| `name` | 是 | 人类可读名称 |
| `category` | 是 | `core` / `lifecycle` / `events` / `research` / `data-quality` / `judgment` |
| `intent` | 是 | 意图词数组，与 `router.md` 保持一致 |
| `inputs` | 是 | 参数定义，含 `type` / `required` / `default` |
| `defaults` | 否 | 阈值与窗口等可调参数，用户可覆盖 |
| `steps` | 是 | 步骤数组，类型见 `core/orchestrator.md` |
| `render` | 是 | `templates/` 下的模板名（不含扩展名） |
| `scheduler` | 否 | 仅监控型工作流使用，指向 `triggers/rules.yaml` |
| `notes` | 否 | 设计说明与 v1 对应关系 |

## steps 合法类型

```
- use: <capability_id>               # 调用已登记能力
  with: {param: "$inputs.xxx"}       # 可选参数覆盖
- parallel: [<capability_id>, ...]   # 并行，内部不得互相依赖
- conditional:
    when: "<简单条件表达式>"
    use: <capability_id>
- branch:
    cases: [{"when": "...", "use": "..."}]
    default: <capability_id>
- loop:
    over: "$inputs.holdings"
    use: <capability_id>
    as: <结果别名>
- include:
    workflow: <workflow_id>
    with: {参数覆盖}
```

## 硬性规则

1. 每个 `use` 必须存在于 `core/capability-registry.yaml`，否则编排器拒绝执行
2. `synthesis` 若出现，必须是**最后一个业务步骤**（其后只能有 `render`）
3. `render` 必须存在于 `templates/`；缺失时回退 `decision_memo` 并说明
4. 不得在 YAML 中写厂商工具名、端点、密钥
5. 不得在 YAML 中定义字段或改写合规条款
6. `include` 展开后不得成环
7. 阈值类参数一律放 `defaults`，便于用户覆盖，不硬编码在条件表达式里
8. 条件表达式只允许简单比较与逻辑组合，不执行任意代码
9. `devils_advocate` 若在 DAG 中出现，必须在 `synthesis` 之前；含 `synthesis` 的判断型工作流应前置反证引擎，纯计算型可只走事实层
10. 判断层工作流的 `render` 必须能呈现四段式与置信度上限
11. `include` 展开时，被调用工作流的 `synthesis` 与 `render` 自动跳过（见 `core/orchestrator.md` 第 10 条），保证全 DAG 至多一个综合层

## 临时拼装

用户指定部分维度时，编排器按 `core/orchestrator.md` 第三节裁剪本 DAG，**不生成新文件**。同一组合反复出现时才提升为正式工作流。

## 场景清单（24 条）

| 分类 | 工作流 |
|---|---|
| core (4) | `a_single_fund` `b_screen` `c_portfolio` `d_monitor` |
| lifecycle (4) | `suitability_check` `fund_replacement` `goal_backsolve` `periodic_review` |
| events (5) | `quarterly_holdings_review` `alert_reassessment` `corporate_action_impact` `manager_change_impact` `periodic_report_deep_read` |
| research (6) | `share_class_breakeven` `pseudo_diversification` `skill_vs_luck` `sponsor_concentration` `manager_narrative_drift` `report_consistency_check` |
| data-quality (2) | `cross_source_verify` `provenance_audit` |
| judgment (3) | `thesis_challenge` `quarterly_calibration` `institutional_evidence` |
