# judgment — 2.0 判断层模块

> 目录仍为 `FAMAS-Skill-v2.0`（保持路径兼容），但**内容版本已升至 2.0.0**：v2.0 的架构层 + v2.0 的判断层同时在此交付。

## 设计立场

**喂研报语料不等于专业度。** Skill 是按需加载的提示词，不是模型权重：塞语料只会挤占上下文、拉高成本、立刻过期，还会把卖方研报的结论先行、事后归因与乐观偏误一起学进去，且有版权与授权边界。

专业度应工程化为四层，本模块负责后三层（L1 已在 `capabilities/synthesis.md` 的四段式中定义并实装）：

| 层 | 内容 | 文件 |
|---|---|---|
| L1 判断框架 | 假设 / 证据 / 反证 / 失效条件；一票否决优先于加权评分 | `framework.md`、`veto-rules.yaml` |
| L2 决策记忆 | 每次判断留痕，季度回看对错并校准 | `decision-log.schema.json`、`calibration.md` |
| L3 机构语料 | 研报 / 财报 / 关键假设表运行时经授权检索，**读而不存** | `institutional-input.md` |
| L4 视角切换 | 同一批事实块，切换结论框架不改数字 | `lenses.yaml` |

反证引擎独立成能力单元 `capabilities/devils_advocate.md`，是 `synthesis` 的强制前置；细则见 `devils-advocate.md`。

## 模块索引

| 文件 | 作用 | 谁读它 |
|---|---|---|
| `framework.md` | 四段式规范、结论强度分级、失败模式 | `synthesis`、`judgment/*` 工作流 |
| `devils-advocate.md` | 五类反证检查清单与置信度上限映射 | `devils_advocate` 能力 |
| `decision-log.schema.json` | 决策记录唯一 schema | `judgment/quarterly_calibration` |
| `calibration.md` | 季度校准六步与误差三层归因 | 同上 |
| `institutional-input.md` | 机构语料运行时检索与引用规范 | `judgment/institutional_evidence` |
| `lenses.yaml` | 视角定义与扩展位 | `synthesis` |
| `veto-rules.yaml` | 一票否决项与阈值 | `synthesis`、`triggers/rules.yaml` |

## 与 v2.0 的关系

- **不新增 persona、不新增 skill 入口**：判断层全部是规则、schema 与能力单元
- **不改变数据层**：事实仍由 `data/gateway.md` 取，判断层不碰厂商工具名、不碰密钥
- **不改变合规闸**：`policies/compliance.md` 仍是输出前唯一强制检查；判断层越"敢下结论"，越依赖这道闸
- **旧工作流自动受益**：`devils_advocate` 已加入所有需要判断力的工作流；纯计算型（如份额临界点）仍可只走事实层

## 硬边界

- 决策日志仅在用户授权下本地持久化，不上传、不入库、不进仓库
- 研报与报告全文运行时读取，读而不存，不打包再分发
- 判断层不产生任何交易信号；越像内行，越不能越过 `policies/compliance.md` 的 C1
