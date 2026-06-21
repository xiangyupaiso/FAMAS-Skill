# Workflow A: 单基金深度分析 (Analyze Single Fund)

## 工作流概述

对用户指定的单只基金进行全方位深度分析，输出综合评级、时机矩阵与风险画像。

## 执行流程

```
用户输入: 基金代码
    |
    v
+----------------------+
| prospectus_analyzer  | --> 解析文档结构
+-----------+----------+
            |
+-----------+-----------+
| performance_analyst  | --> 业绩归因与风险解构
| cost_analyzer        | --> 费率与成本穿透
| manager_profiler     | --> 经理画像(如为主动管理型)
+-----------+----------+
            |
+-----------+-----------+
| macro_strategist     | --> 宏观环境适配度
+-----------+----------+
            |
+-----------v-----------+
| wealth_advisor       | --> 综合评级 + 时机矩阵 + 风险提示
+-----------------------+
```

## 详细步骤

### Step 1: 文档解析 (prospectus_analyzer)

**输入**: 基金代码

**执行**:
- 解析招募说明书：投资范围、业绩基准、费率结构
- 解析最新季报：持有人结构、重仓变化
- 识别特殊条款与限制

**输出**:
```json
{
  "investment_scope": "投资范围摘要",
  "benchmark": "业绩基准",
  "fee_structure": "费率结构",
  "institutional_ratio": "机构持有比例",
  "special_clauses": ["特殊条款"]
}
```

### Step 2: 并行分析 (performance_analyst + cost_analyzer + manager_profiler)

**输入**: 基金代码 + Step 1输出

**并行执行**:

**performance_analyst**:
- 计算收益风险指标
- 分析风格漂移
- 行业归因分析

**cost_analyzer**:
- 显性费率分析
- 隐性成本估算
- 规模惩罚评估

**manager_profiler** (仅主动管理型):
- 经理能力圈分析
- 稳定性评估
- 逆风表现

**输出**:
```json
{
  "performance": { "performance_analyst输出" },
  "cost": { "cost_analyzer输出" },
  "manager": { "manager_profiler输出" }
}
```

### Step 3: 宏观适配 (macro_strategist)

**输入**: 基金策略特征 + Step 2输出

**执行**:
- 评估当前宏观环境
- 分析利率/汇率/政策影响
- 判断风格顺风/逆风

**输出**:
```json
{
  "macro_fit_score": "宏观适配度评分",
  "tailwind_factors": ["顺风因素"],
  "headwind_factors": ["逆风因素"]
}
```

### Step 4: 综合评级 (wealth_advisor)

**输入**: Step 1 + Step 2 + Step 3 全部输出

**执行**:
- 整合所有分析结果
- 计算综合星级(1-5星)
- 生成时机矩阵
- 评估适配投资者类型
- 列出核心风险提示

**输出**:
```json
{
  "star_rating": "4/5星",
  "timing_matrix": "时机矩阵",
  "risk_profile": "风险画像",
  "suitable_for": ["适配投资者类型"],
  "key_warnings": ["核心风险提示"]
}
```

## 最终输出模板

```markdown
## 基金综合分析报告 - {基金代码}

### 一、基础信息
- 基金类型: {类型}
- 业绩基准: {基准}
- 成立日期: {日期}
- 最新规模: {规模}
- 基金经理: {经理} (任职{年限})

### 二、综合评级: {星级}

### 三、时机矩阵
> {时机判断}

### 四、风险画像
- 风险等级: {R1-R5}
- 近3年最大回撤: {回撤}
- 夏普比率: {夏普}
- 风格漂移: {漂移评估}

### 五、适配投资者
- 适合: {适合类型}
- 不适合: {不适合类型}

### 六、核心风险提示
1. {风险1}
2. {风险2}
3. {风险3}

---
*免责声明：本报告仅作信息整理与适配度分析，不构成投资建议。基金过往业绩不预示未来表现。*
```

## 使用示例

```
用户: 请分析基金 020712

系统:
1. 执行 prospectus_analyzer 解析 020712 文档
2. 并行执行 performance_analyst, cost_analyzer, manager_profiler
3. 执行 macro_strategist 评估宏观适配
4. 执行 wealth_advisor 整合输出

输出: 综合评级卡(4/5星) + 时机矩阵 + 适配投资者类型 + 核心风险提示
```
