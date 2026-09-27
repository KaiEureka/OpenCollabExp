# 实验工作流

[English](README.md) | **简体中文**

OpenCollabExp 管理协作算法、角色提示、角色输出 schema、修复策略和方法预设。
Python 定义确定性控制流，OpenCollab 提供公开 Agent 与候选 API。
OpenCollab-Eval 提供候选准备、证据观察、候选捕获和正式评分。

方法面向 OpenCollab 0.8.0 及后续 0.8.x 版本的公开 API，
配合 OpenCollab-Eval 0.8.x 使用。

## 方法选择

`opencollab_exp.methods.CANONICAL_WORKFLOW_METHODS` 以
`opencollab.builtin_workflows:duo` 暴露 OC 公开实现 `duo`。
`WORKFLOW_METHODS` 同时保留 31 个研究工作流与 `generate_review_fix`，共 33 项入口。
`LEGACY_RESEARCH_WORKFLOWS` 标明其中 32 项研究入口。原有 14 个包级导出继续可用。
[方法说明](../../../docs/methods.zh-CN.md) 列出每个注册名称及其执行职责。

G21 固定原有 coder 与 selector 提示，执行交给 OC 公开 `run_dual_coder`。
历史 G22 v2/v3 显式使用保留的 legacy helper，供研究复现。
Duo 与 G22 命令选择 canonical OC 方法。

`workflow_reference(name)` 把方法名转换为 `module:function`。
`load_workflow(name)` 使用 OpenCollab-Eval 通用加载器。
`workflow_options(name)` 提供 `workflow`、`workflow_label` 和
`candidate_environment`。G11 使用 `shared`，lean council 使用 `lean`，
其他方法使用 `isolated`，保持原来的候选准备方式。

```python
from opencollab_exp.methods import load_workflow, workflow_options

method = load_workflow("duo")
options = workflow_options("duo")
```

```bash
python -m opencollab_eval.generation.gen_prediction_workflow \
  --instance-file /path/to/instance.json \
  --output /path/to/predictions.jsonl \
  --workflow opencollab.builtin_workflows:duo \
  --workflow-label duo \
  --candidate-environment isolated
```

工作流选择与 `agent_profile` 分别设置。省略工作流 profile 时沿用所配置的角色行为。
`base`、`default`、`single` 和 `single2` profile 别名映射为 Base/Single2。
独立 Single 默认采用 Base。Solver 预设保持原来的预算、尝试次数、采样值和
外部命令模板。模板现在指向 OpenCollabExp 包中的资源。

## 编写方法

工作流为 async 函数，使用 `opencollab.workflows.workflow` 和公开 context 方法。
角色工具通过 `_public_api.toolset` 使用现有 OpenCollab-Eval
`verification.evaluation_tools` 包装器。

```python
from typing import Any

from opencollab.workflows import workflow

from opencollab_exp.workflows._public_api import toolset


@workflow(name="my-flow", description="Inspect the public task.", phases=["inspect"])
async def my_flow(ctx: Any, args: dict[str, Any]) -> dict[str, Any]:
    goal = str(args.get("goal") or args.get("description") or "").strip()
    await ctx.phase("inspect")
    report = await ctx.agent(
        f"Inspect the repository and report public evidence.\n\n{goal}",
        label="analyst",
        tools=toolset("bash", "file_read", "grep"),
    )
    return {"status": "done" if report else "incomplete", "report": report}
```

新增方法时，在 `WORKFLOW_METHODS` 中登记显式 callable 引用。
私有 helper 模块继续承载共用提示定义与执行函数。
`team-pro` 调用 `analyst-solve`。G22 v2 和 v3 调用保留的 legacy 执行函数，分别传入
selector 和 adjudicator 选择。G20 变体保留 coder 工作流使用的证据交接和候选选择 helper。

## 证据与算法行为

公开题面、候选隔离、角色工具权限、可执行公开测试证据和候选采用保持现有行为。
原生 Bash 命令继续由模型或现有机械重放函数选择。
观察器记录实际命令和测试结果。独立 evaluator 使用保留的评分资源计算正式结果。

`configs/team.self.collab.yaml` 保留用于形成确定性 `self-collab` 方法的提示驱动团队定义。
`configs/team.swebench.yaml` 继续作为 composition 定义。
legacy team shell 资源保持状态 125 的拒绝执行行为，并指向当前生成入口。
