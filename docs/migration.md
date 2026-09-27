# Moving experiment ownership to OpenCollabExp

Experiment methods, deployment commands, campaign scheduling, provider routing
and result presentation now belong to OpenCollabExp. OpenCollab-Eval retains
its evaluation engine and accepts explicit workflow references and solver
configuration from its caller. Pier is selected through its native API in an
independently installed environment.

The OCE companion changes are developed on `codex/extract-experiment-layer`.
OCE's `main` branch remains unchanged. Keep the original main checkout available
and use a separate branch checkout for development with Exp. Install OpenCollab,
that OCE checkout and Exp together as editable packages in an external venv.
The [README](../README.md) provides the installation commands and cache paths.
The paired development versions are OpenCollab 0.8.x and OpenCollab-Eval 0.8.x.
The [SWE Pro-Lite operations](swe-prolite-operations.md) guide preserves the
deployment procedure and operator options.

| Previous experiment entry point | Exp entry point |
| --- | --- |
| `opencollab_eval.commands.duo` | `oc-exp duo` |
| `opencollab_eval.commands.g22` | `oc-exp g22`, the canonical Duo compatibility command |
| `opencollab_eval.commands.swe_g11_parallel_runner` | `oc-exp campaign` |
| `opencollab_eval.commands.swe_v1_prolite_runner` | `oc-exp swe-run` |
| `opencollab_eval.commands.swe_rejudge_queue` | `oc-exp rejudge-queue` |
| `opencollab_eval.commands.package_runtime` | `oc-exp package-runtime` |
| `opencollab_eval.commands.swe_final_report` | `oc-exp final-report` |
| `opencollab_eval.commands.llm_api_proxy` | `oc-exp proxy` |
| Bundled experiment workflow names | `opencollab_exp.methods` and explicit callable references |

The command dispatcher forwards each experiment command's original arguments
to its own parser. Start with the corresponding `--help` and update deployment
scripts to the Exp entry point. G22 and campaign configuration files remain
experiment inputs in the chosen workspace.

The complete registry exposes canonical OC Duo plus 31 retained research
workflows and the review/fix method. `oc-exp methods --json` lists all 33
references. Canonical `duo` references `opencollab.builtin_workflows:duo`; its
`base` role profile resolves to `single2`. The former package exports and
retained strategy variants are described in [methods](methods.md). For a
generic OCE run, pass the selected Exp reference with native OCE's `--workflow`
argument and pass the task JSONL positionally.

```bash
oc-exp run \
  --backend oce \
  --python "$EXP_VENV/bin/python" \
  --cwd "$EXP_WORKSPACE" \
  --output "$EXP_WORKSPACE/backend-logs" \
  --env-file "$EXP_WORKSPACE/provider.env" \
  --dry-run \
  -- run "$EXP_WORKSPACE/tasks.jsonl" \
  --workflow opencollab.builtin_workflows:duo --agent-profile base \
  --output "$EXP_WORKSPACE/oce-results"
```

For Pier, keep the chosen native job file and interpreter. The adapter invokes
its installed `app` entry point and forwards native arguments.

```bash
oc-exp run \
  --backend pier \
  --python "$PIER_PYTHON" \
  --cwd "$EXP_WORKSPACE" \
  --output "$EXP_WORKSPACE/pier-logs" \
  --env-file "$EXP_WORKSPACE/provider.env" \
  --config "$EXP_WORKSPACE/pier-job.json" \
  --dry-run \
  -- run --yes
```

Original candidates, trajectories, scoring reports, Git backups and private
deployment settings remain at their existing storage locations. Reference
these files from the experiment workspace and keep their original instance,
record and scoring identities. New run output goes to the workspace chosen
for that experiment.

Keep dataset roots, DW host configuration, provider environment files and logs
outside tracked source files. The ignored workspace directories are `runs/`,
`artifacts/`, `logs/` and `secrets/`. Existing isolation, official test resources,
evidence handling, process identity and credential protections move with their
responsible implementations. Method and backend selection preserve the
supplied generation, verification and resource settings.

Validate the installation with CLI help, the complete method registry and
fake-child backend tests. The [backend documentation](backends.md) explains
argv, environment precedence, log paths and returned status. A later experiment
uses its explicit task request, backend, data and runtime configuration.
