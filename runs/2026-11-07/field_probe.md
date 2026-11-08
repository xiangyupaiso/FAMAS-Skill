# Wind Alice 连接器首启自检 / 能力探测记录

> 日期：2026-11-07（周六，A 股休市） · 对应工作流：`data-quality/cross_source_verify`（轻量模式）
> **性质声明**：本文件是**一次性会话观测记录**，不是静态映射表。按 `data/gateway.md` 第八节，工具名一律由运行时 `tools/list` 探测，禁止写回仓库作为路由依据；本记录仅用于说明「哪些语义字段当前真的取得到」，实际调用仍以会话内探测结果为准。

## 一、连接状态

| 项 | 结果 |
|---|---|
| 宿主连接器 | `wind-finance` · Wind Alice 万得金融数据 · **已连接、已授权** |
| 登录对象 | 数据源方账号（由宿主客户端完成），FAMAS 不持密钥、无登录入口 |
| 本轮成功调用 | 基金档案、基金业绩、基金持仓、基金财务、基金持有人、指数快照、公告检索（含基金定期报告与招募说明书） |
| 返回形态 | 结构化表（columns + rows，带 unit）/ 公告文档（title + date + doc_type + url + content 片段） |
| 可信度 | 公告与定期报告原文片段 = **L1**；结构化接口 = **L2** |

## 二、38 个语义字段 → 实测覆盖

图例：`OK` 取到可用值 · `PARTIAL` 取到但空值/口径存疑/仅片段 · `MISS` 本轮未取到 · `N/A` 不适用或走豁免

| 语义字段 | 状态 | 实测说明 |
|---|---|---|
| `fund_basic` | OK | 代码、全称、类型、成立日、管理人、托管人 |
| `fund_classification` | PARTIAL | 仅「混合型基金」一级分类；风格属性为空 |
| `benchmark` | OK | 三指数复合基准，档案/季报/中期报告/招募说明书四处一致；**生效日与变更公告未取得，标 `benchmark_version_unverified`**，跨期对照保持 weak |
| `fee_schedule` | PARTIAL | 管理费 1.2%、托管费 0.2%；销售服务费与申赎费档位未取到 |
| `holder_structure` | MISS | 机构/个人比例、户数返回 `null`（季报按规则不披露） |
| `fund_announcements` | OK | 季报（2026-10-27）、招募说明书（2026-11-03 / 2026-05-27 / 2020-10-19），带标题、日期、URL |
| `fund_nav_history` | OK | 补测取得 2026-10-08→2026-11-06 共 22 个交易日单位/累计/复权净值；场外基金走业绩接口净值族 |
| `fund_nav` | OK | 最新 2026-11-06 单位净值 1.4023 元（与累计/复权净值相等） |
| `index_quotes` | OK | 000300.SH 2026-11-06 15:00 快照 |
| `peer_nav` | MISS | 同类排行榜可得，但非净值序列 |
| `holdings` | OK | 2026Q3 十大重仓、占净值比、股票占比 |
| `turnover_history` | MISS | 未取到 |
| `scale_history` | PARTIAL | 2026Q3 资产净值与份额，历史序列未取 |
| `trading_costs` | N/A | `assumption-driven`，按 C7 不输出估算 |
| `fund_universe` | OK | 补测组合条件筛选返回 5 只，目标基金规模 189.3266 亿元与持有人接口一致 |
| `etf_linkage` | MISS | 本轮未测 |
| `manager_roster` | PARTIAL | 3 位经理姓名，但仅 1 个任职日期，无法对应到人 |
| `manager_history` | MISS | 本轮未测 |
| `manager_performance` | MISS | 本轮未测 |
| `macro_rates` | PARTIAL | EDB 通道可用但本账号缺利率类指标权限（S0059749 返回 `code 1008`）；CPI 类指标可提数，属账号授权范围问题 |
| `macro_fx` | MISS | 同上 |
| `style_index` | MISS | 同上 |
| `policy_text` | PARTIAL | 新闻检索可得政策转述（证券日报 2026-11-05），属 L3 二手，非监管原文，需核实原文 |
| `research_reports` | PARTIAL | 补测更正：新闻检索**会返回券商研报摘录**（含机构名/日期/分析师编号），按 L3 + `second_hand` 处理，仅作 `opinion_ref`；非研报全文，关键假设表仍未覆盖 |
| `assumption_tables` | MISS | 同上 |
| `corporate_actions` | MISS | 未测 |
| `dividend_history` | PARTIAL | 分红总额返回 `null`，无法区分「无分红」与「无数据」 |
| `portfolio_input` | N/A | 用户输入字段，非外部取数 |
| `periodic_report_full` | **PARTIAL** | **补测更正**：以完整章节标题可命中 §4.4 原文，但**跨文档误召回严重**（返回的几乎全是其他基金）；目标文档章节仍未命中，须先做 `document_title_match` |
| `manager_commentary` | **MISS** | 目标文档 §4.4 未命中 → `not_retrievable`；命中的其他基金章节一律 `rejected_cross_document` 剔除 |
| `portfolio_report` | PARTIAL | §3.1 / §3.2 章节标题可见，数值与报告内原始行业分类不可得 |
| `financial_statements` | PARTIAL | 结构化接口给 2026H1 / 2025 年报利润与费用；季报财务指标数值片段不可得 |
| `auditor_opinion` | N/A | 本次为季报，按规则不推定存在 |
| `report_holder_changes` | PARTIAL | 季报原文份额总额可得；机构占比变化不可得 |
| `material_events` | MISS | 未取到 |
| `report_fee_detail` | OK | 2026H1 / 2025 管理费、托管费（与合同费率比例交叉验证一致） |
| `prospectus_terms` | OK | 招募说明书投资范围与 12+ 条组合限制原文 |
| `narrative_history` | MISS | 跨期管理人表述序列未取到 |

**统计**：OK 10 · PARTIAL 12 · MISS 13 · N/A 3（共 38）。首版手工统计 9/12/14/3 有误，现由 `tools/validate.py` 第 8 组自动解析本表核对。可读性结论：**单源足以跑通档案、业绩、持仓、费用、条款与合规闸；不足以跑通「说的 vs 做的」「叙事漂移」这类依赖报告章节全文的 2.0 判断场景。**

## 三、本轮跑出的 16 个真实问题（按价值排序）

1. **公告检索超出工具文档描述范围**：工具说明写的是「上市公司公告」，实际能检索到**基金季度报告与招募说明书正文片段**。这使 `periodic_report_reader` 链路从「完全不可跑」变成「部分可跑」。
2. **章节定位不可达**（最大卡点）：三次不同检索式（含指定「4.4」「投资策略与运作分析」「后市展望」）均只返回 §2 基金产品概况。`manager_commentary` / `narrative_history` 必须标 `not_retrievable`，**不能与「未披露」混为一谈**——前者是检索能力边界，后者是披露义务边界。
3. **单位标注错误**：持有人接口的「份额总额」标单位为「份」，数值 1,299,129.2748；季报 §2 原文为 12,991,292,748.11 份。两者相差 10⁴，判定结构化单位应为「万份」。用一手文档消解，记 `unit_mismatch`。
4. **派生指标口径不明**：「持股集中度 0.3541」标单位 `%`，与十大重仓合计 42.6162%（占净值）/ 48.95%（占股票市值）都不吻合，接口未给算法 → 标 `unverified_metric`，不入结论。
5. **同一指标两次调用不一致**：近 1 年回报 -28.578%（窗口未标明）vs -29.1839%（2025-11-07→2026-11-06）。必须显式列 `source_conflicts`，不能静默取一个。
6. **无窗口派生值不可用**：「最新年化收益率 -97.4053%」「最新最大回撤 0」「SHARPE null」与另一组「最大回撤 -33.7931%」「年化波动率 11.253%」相互矛盾。凡未带窗口的派生值应全部弃用。
7. **同类排名必须带分母**：第一次调用只给排名序号（3595/3598/8244…），第二次才给样本总数 9484。无分母的排名不得写入报告。
8. **分母口径不可比**：合同「股票资产占**基金资产** 60%–95%」vs 观测「股票市值占**基金资产净值** 87.0521%」。总资产与净资产不同，按 `periodic_report_reader` 规则只记录、不判定是否落在约束内。
9. **复合基准不能被单一指数替代**：合同基准为三指数加权。工具直接给出复合基准整体表现（YTD -9.7633%、近 1 年 -12.1683%），而沪深300 快照 YTD -12.43% 只是 45% 权重的一个成分。用后者替代会得出错误的相对表现。
10. **休市日快照状态**：运行日 2026-11-07 为周六，接口返回的「交易状态：正常交易中」是 2026-11-06 15:00:06 的快照值。必须标注最近收盘时点，不能表述为「当前盘中」。


11. **跨文档误召回（最高优先级，比字段缺失更危险）**：以完整章节标题检索能取到 §4.4 原文，但 5 条结果里 4 条是招商蓝筹精选、易方达新常态、易方达产业优选、泰信蓝筹精选的同期章节，含「总仓位 90%、港股 36%、A 类增长 26.24%」等数字；目标基金只命中 §3.2。不校验 `title` 就会得到看似有出处、方向完全相反的错误结论（本基金 YTD 实为 -24.7006%）。已实装 `document_title_match` 硬校验与 `cross_document_recall` 否决项（结论判 `invalid`）。
12. **基准版本化**：2026 年《公开募集证券投资基金业绩比较基准指引》过渡期内分批调整超 4000 只产品；实测同管理人旗下易方达价值精选自 2026-07-27、易方达新常态自 2026-06-01 生效新基准（公告片段 L1；证券日报/财通证券研报为二手需核实原文）。`benchmark` 必须带生效日，跨版本区间对照作废 → `benchmark_version_change` 否决项。
13. **指标级权限差异**：同一 EDB 通道内 CPI（M0000612）「仅搜索/仅提数」均可用，10 年国债收益率（S0059749）返回 `code 1008` 无权限。「仅搜索」成功不等于有提数权限，不得据此推算数值；该指标单独进 `missing_fields`。
14. **明显异常量级**：管理人档案返回「基金经理数量 75752 个」，与旗下 557 只产品明显不匹配 → 标 `implausible_value`，不进事实块、不自行猜测修正值。
15. **新闻里夹带研报**：财经新闻检索返回券商研报正文摘录（财通证券 2026-11-01，含 SAC 分析师编号）。工具文档称"不含券商研报"，实际含。按 L3 二手 + 需核实原文，只作 `opinion_ref`，不等同于研报全文或关键假设表已覆盖。
16. **场外/场内接口不可混用**：`get_fund_kline` / `get_fund_quote` / `get_fund_price_indicators` 仅适用场内 ETF/LOF；场外基金（005827.OF）的净值序列必须走业绩接口的净值族。按代码后缀 `.OF` 路由，不能靠名称判断。

## 四点五、补测后新增的可执行规则

上述发现已落成机器可检查的规则，不只是文档说明：

| 规则 | 落点 |
|---|---|
| `document_title_match` / `rejected_cross_document` | `capabilities/periodic_report_reader.md`、`data/gateway.md` 第四节、`judgment/veto-rules.yaml#cross_document_recall` |
| `benchmark_version_break` / `benchmark_version_change` | `data/semantic-fields.yaml#benchmark`、`capabilities/performance_metrics.md`、`judgment/framework.md` |
| `implausible_value` / 指标级权限 / 二手研报 | `data/gateway.md` 第四节、`policies/source-trust.md` 第六/七节 |
| 六类反证（新增来源身份反证） | `capabilities/devils_advocate.md` |
| 单源降级（同源内部一致性） | `workflows/data-quality/cross_source_verify.yaml` |
| 输出闸（禁止词 + 元描述豁免 + 溯源 + 口径 + 文档身份 + 基准版本） | `tools/check_report.py` |
| 结构一致性（版本、provider 声明、规则锚点、覆盖表统计） | `tools/validate.py` 第 8 组 |

## 四、本轮对仓库的修复（见同目录与各文件）

| # | 修复 | 位置 |
|---|---|---|
| 1 | 新增已验证 provider 声明（只写能力类别与 coverage，不写工具名路由） | `data/providers/wind-alice.yaml` |
| 2 | 口径归一新增「单位错标 / 无窗口派生值 / 无分母排名 / 分母不可比」四条规则 | `data/gateway.md` 第四节 |
| 3 | 契约新增 `not_retrievable_sections`，与 `not_disclosed_sections` 区分 | `contracts/famas.contract.json` + `templates/periodic_report_memo.md` |
| 4 | 报告阅读能力新增「章节检索不可达」状态与禁止推测条款 | `capabilities/periodic_report_reader.md` |
| 5 | 字段字典为 `periodic_report_full` / `manager_commentary` 补检索粒度说明 | `data/semantic-fields.yaml` |
| 6 | SETUP 增加「已验证连接器」引导；README 验证章节记录首跑结论 | `SETUP.md` / `README.md` / `MIGRATION.md` |

## 五、仍未验证

- 补测已完成：全市场筛选、管理人公司档案、场外净值序列、EDB 通道、财经新闻。仍标 `MISS` 的是 `manager_history` / `manager_performance` / `etf_linkage` / `turnover_history` / `corporate_actions` / `assumption_tables` / `material_events` / `narrative_history` / `holder_structure` 等，属本轮未取到或未覆盖，不是数据源不支持。
- 未测试多源交叉校验（当前只连了 1 个数据源）；`source_conflicts` 本轮全部来自**同源不同调用**，不是跨源分歧。
- 决策日志本地持久化（2.0 L2）按设计默认不落盘，本轮未启用。
- 机构研报 / 关键假设表（2.0 L3）无授权源，本轮未接入。

---

本报告仅作信息整理与适配度分析，不构成投资建议。基金过往业绩不预示未来表现。市场有风险，投资需谨慎。
