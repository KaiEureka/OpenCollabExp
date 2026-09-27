# Methods and presets

**English** | [简体中文](methods.zh-CN.md)

Experiment methods are explicitly registered in `opencollab_exp.methods`. The canonical `duo` entry loads `opencollab.builtin_workflows:duo` from OC 0.8.0. The 31 research workflows and the review/fix method remain loadable, for 33 total entries. The former 14 package exports remain available, and the 17 previously omitted strategies can be selected by name.

| Name | Former export status | Family |
| --- | --- | --- |
| `duo` | OC public built-in | Canonical Duo |
| `analyst-solve` | Package export | Analyst / TeamPro |
| `base-team` | Package export | Base |
| `base-team-single-pass-v1` | Package export | Base |
| `candidate-tournament-council-v1` | Retained variant | Evidence experiments |
| `evidence-action-council-v1` | Retained variant | Evidence experiments |
| `evidence-critic-repair-v1` | Retained variant | Evidence experiments |
| `scout-solve` | Package export | Self / Split / Scout |
| `self-collab` | Package export | Self / Split / Scout |
| `split-solve` | Package export | Self / Split / Scout |
| `swe-committee-v2` | Package export | Committee |
| `team-pro` | Package export | Analyst / TeamPro |
| `validation-council-dual-coder-contract-v1` | Package export | G21 / G22 |
| `validation-council-dual-coder-selection-v2` | Package export | G21 / G22 |
| `validation-council-dual-coder-selection-v3` | Package export | G21 / G22 |
| `validation-council-g20-coder-contract-v1` | Retained variant | G20 + coder |
| `validation-council-g20-coder-red-green-v1` | Retained variant | Red Green |
| `validation-council-g20-coder-red-green-v2` | Retained variant | Red Green |
| `validation-council-g20-coder-safe-v1` | Retained variant | G20 + coder |
| `validation-council-lean-official-v1` | Package export | Lean council |
| `validation-council-solve` | Package export | G11 |
| `validation-council-triple-coder-contract-v1` | Package export | Triple |
| `validation-council-wired-coder-heavy-v1` | Retained variant | G20 wired |
| `validation-council-wired-conditional-repair-v1` | Retained variant | G20 wired |
| `validation-council-wired-diagnose-repair-v1` | Retained variant | G20 wired |
| `validation-council-wired-dual-contract-v1` | Retained variant | G20 candidate |
| `validation-council-wired-dual-g20-v1` | Retained variant | G20 candidate |
| `validation-council-wired-plus-v1` | Retained variant | G20 wired |
| `validation-council-wired-red-rescue-v1` | Retained variant | G20 candidate |
| `validation-council-wired-resilient-v1` | Retained variant | G20 wired |
| `validation-council-wired-tournament-v1` | Retained variant | G20 candidate |
| `validation-council-wired-v1` | Retained variant | G20 wired |
| `generate_review_fix` | Former default strategy | Review/fix |

`workflow_reference` accepts a method name or an explicit `module:function` reference. `workflow_options` produces the callable reference, display label, and candidate environment for the evaluation generator. G11 retains `shared` and the lean council retains `lean`. Other strategies use `isolated`. The evaluation core executes the reference through its generic loader while the experiment package owns method selection and role parameters.

`DEFAULT_WORKFLOW_SOLVERS` retains the existing presets for `g11`, `g1.1`, `g20-exp1`, `g20-exp2`, `g11-wired`, `baseTeam`, `TeamPro`, `openhands`, and `claude-code`. `WorkflowSolverSpec` is supplied by OpenCollab-Eval; names, budgets, model settings, and external command templates belong to OpenCollabExp. The three previously unresolved G20 targets now load through the complete registry.

The role graphs and helper functions move together under `workflows`. G21 delegates to the public OC `run_dual_coder` with its fixed prompts. Historical G22 v2 and v3 retain the legacy control flow, Red-Green v2 keeps the v1 selection and adoption rules, and TeamPro continues to delegate to the analyst method. Existing role permissions, public evidence validation, and candidate adoption rules are retained. Method tests cover these behaviors with scripted responses and synthetic source programs.

`CANONICAL_WORKFLOW_METHODS` identifies the OC-owned default. `LEGACY_RESEARCH_WORKFLOWS` identifies the 32 retained experiment entries. Selecting `duo` uses the same OC function object as its built-in registry.
