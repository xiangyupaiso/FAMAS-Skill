# FAMAS — 基金智选分析系统

本项目包含 FAMAS (Fund Analysis Multi-Agent System) 的自定义 Skills，可在 OpenAI Codex CLI 中直接使用。

## 可用 Skills

| Skill | 用途 | 触发词 |
|-------|------|--------|
| `famas-analyze-fund` | 单基金深度分析 | 分析基金、基金评级、基金分析 |
| `famas-screen-fund` | 行业/偏好筛选 | 筛选基金、找基金、基金对比 |
| `famas-diagnose-portfolio` | 组合持仓诊断 | 诊断持仓、组合诊断、再平衡 |
| `famas-monitor-fund` | 持续监控预警 | 监控基金、基金预警、异动提醒 |

## 合规约束

- 严禁输出"买入"/"卖出"/"加仓"/"减仓"/"清仓"等明确交易信号
- 所有评级输出必须附带核心风险提示
- 输出框架为"适配度"而非"推荐度"
- 必须包含标准免责声明
