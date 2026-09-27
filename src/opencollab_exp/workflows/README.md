# Experiment workflows

**English** | [简体中文](README.zh-CN.md)

OpenCollabExp owns the collaboration algorithms, role prompts, role output schemas,
repair policies, and method presets. Python defines deterministic control flow while
OpenCollab provides the public agent and candidate APIs. OpenCollab-Eval supplies
candidate preparation, evidence observation, candidate capture, and official scoring.

The methods target the public API in OpenCollab 0.7.0 and later 0.7.x releases,
paired with OpenCollab-Eval 0.7.x.

## Method selection

`opencollab_exp.methods.WORKFLOW_METHODS` registers all 31 retained workflow names and
`generate_review_fix`. The former 14 package exports remain available with their
original callable identities. The 17 variants previously omitted from the bundled
generator registry are selectable through their method names and explicit references.
[Methods](../../../docs/methods.md) lists every registered name and its execution role.

`workflow_reference(name)` resolves a method to `module:function`.
`load_workflow(name)` uses the generic OpenCollab-Eval loader.
`workflow_options(name)` supplies `workflow`, `workflow_label`, and
`candidate_environment`. G11 uses `shared`, the lean council uses `lean`, and other
methods use `isolated`, preserving their candidate preparation choices.

```python
from opencollab_exp.methods import load_workflow, workflow_options

method = load_workflow("validation-council-dual-coder-selection-v2")
options = workflow_options("validation-council-dual-coder-selection-v2")
```

```bash
python -m opencollab_eval.generation.gen_prediction_workflow \
  --instance-file /path/to/instance.json \
  --output /path/to/predictions.jsonl \
  --workflow opencollab_exp.workflows.validation_council_solve:validation_council_solve \
  --workflow-label validation-council-solve \
  --candidate-environment shared
```

Workflow choice and `agent_profile` are independent. `single` selects the default
OpenCollab role driver and `single2` selects Single2 for every role. Solver presets
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
`team-pro` calls `analyst-solve`. G22 v2 and v3 call the G21 execution function with
selector and adjudicator choices. G20 variants retain their evidence handoff and
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
