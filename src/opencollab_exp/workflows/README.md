# Experiment workflows

**English** | [简体中文](README.zh-CN.md)

OpenCollabExp owns the collaboration algorithms, role prompts, role output schemas,
repair policies, and method presets. Python defines deterministic control flow while
OpenCollab provides the public agent and candidate APIs. OpenCollab-Eval supplies
candidate preparation, evidence observation, candidate capture, and official scoring.

The methods target the public API in OpenCollab 0.8.0 and later 0.8.x releases,
paired with OpenCollab-Eval 0.8.x.

## Method selection

`opencollab_exp.methods.CANONICAL_WORKFLOW_METHODS` exposes `duo` as
`opencollab.builtin_workflows:duo`, the public OC implementation.
`WORKFLOW_METHODS` also retains the 31 research workflows and `generate_review_fix`,
for 33 available entries. `LEGACY_RESEARCH_WORKFLOWS` identifies those 32 research
entries. The original 14 package exports remain available.
[Methods](../../../docs/methods.md) lists every registered name and its execution role.

G21 keeps its fixed coder and selector prompts and delegates execution to the public
OC `run_dual_coder`. Historical G22 v2/v3 explicitly use retained legacy helpers for
research reproduction. The Duo and G22 commands select the canonical OC method.

`workflow_reference(name)` resolves a method to `module:function`.
`load_workflow(name)` uses the generic OpenCollab-Eval loader.
`workflow_options(name)` supplies `workflow`, `workflow_label`, and
`candidate_environment`. G11 uses `shared`, the lean council uses `lean`, and other
methods use `isolated`, preserving their candidate preparation choices.

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

Workflow choice and `agent_profile` are independent. An omitted workflow profile
preserves configured role behavior. The `base`, `default`, `single`, and `single2`
profile aliases resolve to Base/Single2. Standalone Single defaults to Base. Solver presets
retain their prior budgets, attempts, sampling values, and external command templates.
The templates now point to resources packaged in OpenCollabExp.

## Authoring

Workflows are async functions using `opencollab.workflows.workflow` and its public
context methods. Role tool sets are provided by the existing OpenCollab-Eval
`verification.evaluation_tools` wrapper through `_public_api.toolset`.

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

Register an explicit callable reference in `WORKFLOW_METHODS` when adding a method.
Private helper modules retain shared prompt definitions and execution functions.
`team-pro` calls `analyst-solve`. G22 v2 and v3 call the retained legacy execution
function with selector and adjudicator choices. G20 variants retain their evidence handoff and
candidate selection helpers used by the coder workflows.

## Evidence and algorithm behavior

Public task inputs, candidate isolation, role tool permissions, executable public
test evidence, and candidate adoption preserve their existing behavior. Native Bash
commands remain selected by the model or by an existing mechanical replay function.
The observer records actual commands and test results. Official resolution is
computed by the independent evaluator using the retained scoring resources.

`configs/team.self.collab.yaml` preserves the prompt-driven team definition used to
derive the deterministic `self-collab` method. `configs/team.swebench.yaml` remains a
composition definition. The legacy team shell resources retain their status 125
rejection and point to current generation entrypoints.
