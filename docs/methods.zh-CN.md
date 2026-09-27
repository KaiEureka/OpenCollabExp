# 方法与预设

[English](methods.md) | **简体中文**

实验方法在 `opencollab_exp.methods` 中显式登记。31 种工作流和 review/fix 均可加载。原 14 项包级导出保留，此前缺少导出的 17 种策略也支持按名称选择。

| 名称 | 原导出状态 | 方法族 |
| --- | --- | --- |
| `analyst-solve` | 包级导出 | Analyst / TeamPro |
| `base-team` | 包级导出 | Base |
| `base-team-single-pass-v1` | 包级导出 | Base |
| `candidate-tournament-council-v1` | 保留变体 | Evidence experiments |
| `evidence-action-council-v1` | 保留变体 | Evidence experiments |
| `evidence-critic-repair-v1` | 保留变体 | Evidence experiments |
| `scout-solve` | 包级导出 | Self / Split / Scout |
| `self-collab` | 包级导出 | Self / Split / Scout |
| `split-solve` | 包级导出 | Self / Split / Scout |
| `swe-committee-v2` | 包级导出 | Committee |
| `team-pro` | 包级导出 | Analyst / TeamPro |
| `validation-council-dual-coder-contract-v1` | 包级导出 | G21 / G22 |
| `validation-council-dual-coder-selection-v2` | 包级导出 | G21 / G22 |
| `validation-council-dual-coder-selection-v3` | 包级导出 | G21 / G22 |
| `validation-council-g20-coder-contract-v1` | 保留变体 | G20 + coder |
| `validation-council-g20-coder-red-green-v1` | 保留变体 | Red Green |
| `validation-council-g20-coder-red-green-v2` | 保留变体 | Red Green |
| `validation-council-g20-coder-safe-v1` | 保留变体 | G20 + coder |
| `validation-council-lean-official-v1` | 包级导出 | Lean council |
| `validation-council-solve` | 包级导出 | G11 |
| `validation-council-triple-coder-contract-v1` | 包级导出 | Triple |
| `validation-council-wired-coder-heavy-v1` | 保留变体 | G20 wired |
| `validation-council-wired-conditional-repair-v1` | 保留变体 | G20 wired |
| `validation-council-wired-diagnose-repair-v1` | 保留变体 | G20 wired |
| `validation-council-wired-dual-contract-v1` | 保留变体 | G20 candidate |
| `validation-council-wired-dual-g20-v1` | 保留变体 | G20 candidate |
| `validation-council-wired-plus-v1` | 保留变体 | G20 wired |
| `validation-council-wired-red-rescue-v1` | 保留变体 | G20 candidate |
| `validation-council-wired-resilient-v1` | 保留变体 | G20 wired |
| `validation-council-wired-tournament-v1` | 保留变体 | G20 candidate |
| `validation-council-wired-v1` | 保留变体 | G20 wired |
| `generate_review_fix` | 原默认策略 | Review/fix |

`workflow_reference` 接受方法名或显式 `module:function` 引用。`workflow_options` 输出评测生成器的引用、友好名称和候选环境。G11 的 `shared` 与 lean council 的 `lean` 设置保持原行为，其他策略使用 `isolated`。评测核心通过通用加载器执行引用，方法选择和角色参数由实验包持有。

`DEFAULT_WORKFLOW_SOLVERS` 保留 `g11`、`g1.1`、`g20-exp1`、`g20-exp2`、`g11-wired`、`baseTeam`、`TeamPro`、`openhands` 和 `claude-code` 的现有预设。数据类型 `WorkflowSolverSpec` 来自 OpenCollab-Eval，具体名称、预算、模型设置和外部命令模板来自 OpenCollabExp。此前三个无法解析的 G20 target 现在通过完整注册表加载。

`workflows` 中的角色图与辅助函数整体迁移。G22 v2、v3 继续复用 G21 控制流，Red-Green v2 继续复用 v1 的选择与采用规则，TeamPro 继续转发 analyst 方法。原有角色权限、公开证据验证与候选采用规则保留。方法测试使用脚本化返回值和合成源程序覆盖这些行为。
