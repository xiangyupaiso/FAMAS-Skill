# DataGateway — MCP 数据层规范

> 打通「MCP 数据层 → FAMAS」的唯一通道。Core 与工作流只认**语义字段**，不认厂商、不认工具名、不认端点。

---

## 一、职责边界

| 组件 | 职责 |
|---|---|
| `workflows/*.yaml` | 声明 `requires: [语义字段...]` |
| `data/semantic-fields.yaml` | 定义每个语义字段的含义、口径、最小可信等级、时效要求 |
| `data/providers/*.yaml` | 声明某厂商大致覆盖哪些能力类别、授权方式、可信等级、优先级 |
| **DataGateway（本文件）** | 选源 → 运行时探测工具 → 建立字段映射 → 取数 → 口径归一 → 冲突检测 → 输出带 provenance 的事实块 |
| `policies/source-trust.md` | 可信度分级、冲突处理、降级规则 |

**关键设计：工具名不硬编码。** 各厂商 MCP 的工具集合会变、账号开通范围因人而异，唯有运行时 `tools/list` 是事实来源。provider 文件只写 `capability_hints`（能力类别提示），不写 `tool_names`。

---

## 二、取数链路（六步）

```
1 收集请求    汇总本次 DAG 所有能力的 requires，去重
2 选源        按 provider.priority 与字段 trust_min 过滤；未连接/未授权/scope 不足的源剔除
3 探测        对候选源调用 tools/list，取得本次会话真实可用的工具清单
4 映射        按 capability_hints 与工具描述，生成 语义字段 -> 工具名 + 参数 的临时映射表
5 取数        执行调用；口径归一（单位、复权、频率、报告期、份额类别、时区）
6 质检        冲突检测、时效校验、provenance 注入 -> 输出事实块
```

映射表只在会话内存活，**不写回仓库**。同一字段多源可得时按 `policies/source-trust.md` 处理，不静默取一个。

---

## 三、选源规则

```
候选 = 已连接 && 已授权 && 该字段在 coverage 中 && trust >= field.trust_min && trust >= capability.trust_min
排序 = trust 升序(L1 优先) -> provider.priority 升序 -> 本次会话已成功调用过的源优先
执行 = 取首个；失败则按降级路径尝试次优源
```

- 能力注册表的 `trust_min` 与字段的 `trust_min` **取更严者**
- 未通过过滤的字段 → 写入 `missing_fields`，依赖它的计算跳过
- 不允许为了满足字段而降低可信度等级
- **混合可信度 provider**（2026-11-07 首跑新增）：同一连接器可同时提供一手披露文件与结构化接口。若 provider 声明了 `trust_by_source_type`，选源时按**字段所走的来源类型**取对应等级，而不是按 `trust` 整体值一刀切。例：公告 / 定期报告 / 招募说明书原文片段走 `disclosure_original: L1`，档案 / 业绩 / 持仓 / 财务等结构化接口走 `structured_api: L2`。否则 `trust_min: L1` 的字段会被一个整体标 L2 的源错误过滤。
- **假设驱动字段**（`source_type: assumption-driven`，如 `trading_costs`）：不从 provider 取数，允许没有 coverage 声明；由能力单元使用 `assumptions` 默认参数计算，输出标 `estimated: true` 并列入 `missing_fields` 提示，不得伪装成实测数据

---

## 四、口径归一（冲突高发区）

| 项目 | 统一口径 |
|---|---|
| 证券代码 | 场内基金 6 位数字；港股 5 位；美股 ticker；逐个核对，不靠名称匹配 |
| 复权 | 净值序列统一标明前复权/后复权/不复权；不同来源不一致则列分歧 |
| 频率 | 日频/周频/月频显式标注，不做隐式重采样 |
| 时区 | 相对时间按北京时间解释；跨市场比较先对齐窗口 |
| 报告期 | 持仓统一带 `report_period`（YYYYQn），跨期重合度计算禁止 |
| 单位 | 规模统一为亿元；费率统一为年化百分比；比例统一为小数或百分数并标注 |
| 权重 | 组合权重合计须为 100%，不自动归一化 |

### 实测口径陷阱（2026-11-07 首跑新增，逐条强制）

| 陷阱 | 规则 |
|---|---|
| 单位标注错误 | 结构化值的 `unit` 与一手文档不一致时，**以一手文档为准**并标 `unit_mismatch`。例：份额总额返回 1,299,129.2748 标「份」，季报原文为 12,991,292,748.11 份 → 判定实际单位为「万份」 |
| 口径未说明的派生指标 | 无计算口径且与可加总明细不吻合的派生值（如标 `%` 的「持股集中度」与十大合计不符）→ 标 `unverified_metric`，**不得进入事实块或结论** |
| 无窗口 / 无分母 | 未带统计窗口的收益率、年化值、最大回撤，以及未带样本总数的同类排名 → 一律弃用；带窗口且带分母的版本优先，另一值列入 `source_conflicts` |
| 分母不可比 | 条款分母与观测分母不同（「占基金资产」vs「占基金资产净值」）→ 记录原文与观测值，标「分母口径不一致，不判定」，不作定性判断 |
| 复合基准替代 | 合同基准为多指数加权时，**不得用其中一个指数快照替代**；优先取数据源给出的复合基准整体表现，单指数只作市场环境补充并标注权重 |
| 章节检索不可达 | 文档级检索只能取到部分片段时，缺章节标 `not_retrievable`（见 `capabilities/periodic_report_reader.md`），不得与 `not_disclosed` 混用 |
| 休市日快照 | 非交易日的行情快照字段（如「交易状态：正常交易中」）是最近交易收盘时点的状态，必须标注快照时间与休市，不得表述为当前盘中 |
| **文档身份误召回** | 文档检索返回的章节片段**可能来自其他基金**。进入事实块前逐条校验 `title` 含目标基金全称/简称、报告类型、报告期、披露日期；任一不匹配标 `rejected_cross_document` 整条丢弃。名称相近（如同为"XX蓝筹精选"）、同管理人、同报告期的产品尤其危险。命中见 `judgment/veto-rules.yaml#cross_document_recall`，结论判 `invalid` |
| 基准版本 | `benchmark` 是版本化字段：取数须带生效日与变更公告。报告期内发生变更时跨期对照标 `benchmark_version_break`，禁止用新基准回算旧区间；命中 `benchmark_version_change` 否决项 |
| 明显不合理数值 | 结构化字段出现量级明显异常的值（如「基金经理人数 75752 个」）→ 标 `implausible_value`，不进事实块、不进结论，列入 `data_quality_flags`；不得自行"修正"为猜测值 |
| 指标级权限差异 | 同一通道内部分指标可用、部分返回无权限（如宏观 EDB `code 1008`）：只把无权限指标列入 `missing_fields`，不影响其他指标；「仅搜索」成功不等于「仅提数」有权限，不得据此推算数值 |
| 二手研报片段 | 新闻检索返回的券商研报摘录按 L3 + `second_hand: true` + "需核实原文"，只作 `opinion_ref`；不得等同于研报全文或关键假设表已覆盖，也不得与 L1 公告并列不标等级 |

---

## 五、provenance 注入

每次成功取数后，网关为字段附加：

```
source       机构/厂商名 + 报告或接口名
as_of        数据时点（YYYY-MM-DD 或 YYYYQn）
release_date 发布日期（若与 as_of 不同）
confidence   L1 | L2 | L3（L4 禁止）
estimated    是否估算
second_hand  是否非一手转述
method       计算方法与参数假设
```

字段契约见 `contracts/famas.contract.json#/$defs/provenance`。**没有 provenance 的数值不得进入事实块**。

---

## 六、降级路径

```
源未连接 / 401 / scope 不足
  -> 提示 SETUP.md 对应章节（Skill 不代登录、不持密钥）
  -> 尝试次优源
  -> 仍失败：字段进入 missing_fields，报告输出"数据源未覆盖"
全部源不可用
  -> 只输出分析框架与待补字段清单，不输出任何数值结论
```

限流/额度：遵循能力 `cache_ttl` 与字段 `freshness`，避免重复调用；不绕过厂商限流。

---

## 七、新增数据源（换源不改工作流）

1. 在 `data/providers/` 新增一个 YAML，声明 `id`、`auth`、`trust`、`priority`、`capability_hints`、`coverage`
2. 在 `mcp.json` 模板里加一段占位配置，在 `SETUP.md` 补一节登录引导
3. 首启自检（`data-quality/cross_source_verify` 轻量模式）确认字段覆盖
4. **不需要改动任何工作流、能力单元、模板或合规文件**

---

## 八、禁止

- 在 Core / 工作流 / 能力单元里硬编码厂商工具名、端点、密钥
- 把 `tools/list` 探测结果写回仓库当静态映射
- 用模型记忆或估算值填补取不到的数值
- 静默采用冲突来源中的某一个
- 缓存或再分发研报、行情明细到仓库
- 把 L3 抓取数据与 L1 公告并列而不标等级
