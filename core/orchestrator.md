# Core — 编排器规则

> 定义声明式工作流 YAML 的执行语义。工作流只声明"做什么"，不写"怎么做"；具体计算口径在 `capabilities/*.md`。

## 一、步骤类型

| 类型 | 语义 | 示例 |
|---|---|---|
| `use` | 调用单个能力 | `use: cost_model` |
| `parallel` | 并行调用多个能力，全部返回后汇合 | `parallel: [performance_metrics, cost_model]` |
| `conditional` | 条件成立才执行 | `conditional: {when: "fund.type == 'active'", use: people}` |
| `branch` | 互斥分支，`default` 必填 | 见下方 |
| `include` | 内联展开另一条工作流（可带参数覆盖） | `include: {workflow: core/a_single_fund, with: {fund_code: "$alert.fund_code"}}` |
| `loop` | 对集合逐项执行同一能力，结果聚合 | `loop: {over: "$holdings", use: fund_profile, as: profiles}` |
| `render` | 指定输出模板并结束 | `render: rating_card` |

## 二、执行约束

1. **DAG 校验**：展开 `include` 后检测环；有环直接报错并指出环路，不执行。
2. **能力校验**：每个 `use` 必须存在于 `core/capability-registry.yaml`；校验其 `inputs` 已由上游或用户提供、`requires` 的语义字段已声明、`trust_min` 可被当前数据源满足。
3. **并行独立性**：`parallel` 内的能力不得互相依赖对方输出；需要依赖的必须拆到后续步骤。
4. **失败隔离**：单个能力失败时标记该块 `missing_fields`，其余能力继续执行；最终报告显式列出缺口。**严禁填补估算值**。
5. **缓存**：按能力 `cache_ttl` 复用同参数结果；跨用户不共享缓存；行情类字段 ttl 由 `data/semantic-fields.yaml` 的时效性要求决定。
6. **幂等**：同一 `workflow_id + 参数 + 数据截止时间` 重复执行应得到一致结果。
7. **noop 合法**：`branch.default: noop` 与条件为假时的跳过都是合法空操作，不触发能力校验，但必须在报告中记录「已跳过 + 原因」。
8. **轻量模式**：`data-quality/cross_source_verify` 在 `fields` 为空时进入首启自检模式，跳过全部取数步骤，只做数据源探测、字段覆盖与映射冲突报告（见 `SETUP.md` 第 5 节）。
9. **判断层顺序**：`devils_advocate` 必须在 `synthesis` 之前，且 `synthesis` 的 `counter_evidence` 段只能引用其输出；纯计算型工作流可只走事实层。判断层规则见 `judgment/framework.md`。
10. **include 的 synthesis 抑制**：内联展开被调用工作流时，其 `synthesis` 与 `render` 步骤**自动跳过**，只保留事实层与判断层步骤；由最外层 DAG 唯一的 `synthesis` 统一收口。因此任意展开后的 DAG **至多含一个 `synthesis`**，且它必须是最后一个业务步骤。被跳过的事实块仍完整进入 `$steps` 供最外层消费。

> 这条规则是编排 dry-run 验证发现的：`core/d_monitor`、`lifecycle/periodic_review`、`events/alert_reassessment` 三条链路原本都通过 `include` 引入含 `synthesis` 的子工作流，展开后会出现两个综合层，违反"唯一允许输出观点的能力"。抑制规则保证闭环链路复用事实块而不重复下结论。

## 三、临时拼装（自由组合的关键）

用户指定部分维度时，Core 不新增工作流，而是对命中的工作流做 DAG 裁剪：

```
规则 A  用户点名能力（"只看费率"）→ 保留被点名能力及其必要上游，裁剪其余分支
规则 B  用户点名输出（"给我一张对比表"）→ 保留 relative_compare，替换 render 模板
规则 C  用户给出新组合（"把监控接到评级"）→ 生成临时 DAG，仅由已登记能力构成
规则 D  裁剪后 DAG 为空或含未登记能力 → 停止并说明，不杜撰角色
```

临时 DAG 只在本次会话有效，**不写入仓库**；若同一组合被反复使用，再提升为正式工作流 YAML。

## 四、参数覆盖与变量

- 变量引用统一用 `$`，如 `$inputs.fund_code`、`$steps.performance.sharpe_ratio`
- `with` 中的覆盖只作用于本次 `include`，不污染被调用工作流的定义
- 用户参数优先级 > 工作流默认值 > 能力默认值
- **参数继承**：步骤未显式写 `with` 时，按「同名 inputs → 上游同名输出块 → 能力默认值」自动注入；仍缺失则标 `missing_fields`，不静默留空
- **上下文透传**：`synthesis` 可接收 `investor_profile`、`alert_context`、`baseline_report_ref`、`report_ref` 等上下文参数作为判断背景；这些参数只参与推理，不写入契约输出块（`decision_log_ref` / `opinion_refs` 除外）

## 五、条件表达式

仅允许简单比较与逻辑组合，不执行任意代码：

```
fund.type == 'active'
$inputs.horizon >= 3
$steps.cost.tcr_3y > $steps.cost.peer_median
$source.trust >= 'L2'
```

条件求值为假时该步骤跳过，并在报告中记录"已跳过 + 原因"。

## 六、降级

- 数据源不可用：见 `core/SKILL.md` 第六节与 `policies/source-trust.md`
- 能力所需字段缺失：跳过该计算，不阻断整条工作流
- `render` 模板缺失：回退到 `templates/decision_memo.md`，并说明模板缺失

## 七、监控型工作流

`core/d_monitor` 与 `triggers/rules.yaml` 配合：Core 本身不被定时唤醒，由宿主调度器按 `check_interval` 触发一次 `core/d_monitor` 执行。命中规则时生成 `alert` 对象，并可自动 `include: events/alert_reassessment` 形成闭环。Skill 文件不持有定时器、不常驻进程。

## 八、禁止

- 在工作流里复制能力定义或合规条款
- 在 YAML 里硬编码厂商工具名、端点、密钥
- 用 `include` 无限递归或跨分类循环引用
- 用自然语言步骤描述代替 `use`（"让分析师看一下"不是合法步骤）
