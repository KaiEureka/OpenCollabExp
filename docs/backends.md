# Native backend adapters

OpenCollabExp owns each experiment's working directory, configuration paths and
log directory. A backend adapter invokes an independently installed OCE or Pier
CLI through an explicitly selected Python interpreter. Backend choice belongs
to the experiment configuration.

```python
from pathlib import Path

from opencollab_exp.backends import BackendConfig, run_backend

invocation = BackendConfig(
    backend="oce",
    python="/opt/oce/bin/python",
    cwd=Path("/srv/experiments/example"),
    artifact_dir=Path("backend-logs"),
    argv=("run", "tasks.jsonl", "--output", "oce-results"),
    env_file=Path("provider.env"),
)
result = run_backend(invocation)
print(result.returncode, result.stdout_path, result.stderr_path)
```

OCE uses the module `opencollab_eval`. Its subcommand and arguments come from
`argv`. The companion OCE branch accepts `run TASKS_JSONL`, with model and
provider settings supplied through native flags or the environment. Keep the
adapter's `config` field unset for this native command. Workflow callables are
selected with OCE's `--workflow module:function` argument.

The paired versions are OpenCollab 0.8.x and OpenCollab-Eval 0.8.x. Select
canonical OC Duo with `--workflow opencollab.builtin_workflows:duo` and the
`base` role profile, which resolves to `single2`. The experiment command
`oc-exp duo` deploys the same canonical workflow; `oc-exp g22` is its
compatibility name. Retained research methods use their explicit callable
references. The adapter forwards the chosen profile and budget arguments.

Pier calls its native application through `pier.cli.main.app`. The adapter uses
`python -c 'from pier.cli.main import app; app()'`. For a native job configuration,
select `backend="pier"`, `python="/opt/pier/bin/python"`, `argv=("run",)` and
`config=Path("job.json")`. Install the chosen Pier distribution in that
interpreter's environment. The job file retains dataset, agent, resource,
generation and verification settings exactly as supplied.

| Configuration field | Meaning |
| --- | --- |
| `backend` | `oce` or `pier` |
| `python` | Explicit Python interpreter, including an absolute venv path |
| `cwd` | Working directory for the native invocation |
| `artifact_dir` | Directory containing `stdout.log` and `stderr.log` |
| `argv` | Native CLI subcommand and arguments as a sequence of strings |
| `config` | Optional native job/config path appended as `--config PATH` |
| `module` | Optional Python module override invoked with `python -m MODULE` |
| `env_file` | Optional file containing literal environment assignments |
| `env` | Environment values that override both inherited values and the env file |

Relative config, environment-file and artifact paths are interpreted from
`cwd`. Prepare the working directory and job/config before execution. When
the native CLI uses a different config flag, include that flag and path in
`argv` and leave the `config` field unset. `build_argv(invocation)` returns the
exact argument list for inspection or an experiment-level dry run.

The subprocess receives an argv list with `shell=False`. Arguments, including
resource limits and scoring options, pass directly to the selected CLI. The
adapter reads the config path as an argument and leaves the file's contents
unchanged. Generation and verification budgets are therefore controlled by
the supplied native configuration and arguments.

Environment files support `NAME=value`, an optional `export` prefix, quoted
values, blank lines and comments. Values are literal. Variable expansion and
command substitution are outside this format. Environment-file values
override inherited environment values, and `env` overrides both. Keep provider
credentials in the environment file or environment mapping. The adapter's
result and configuration representation omit environment values. Native stdout
and stderr are appended directly to the selected log files, so each native
backend remains responsible for its own output handling.

`BackendResult.returncode` preserves the native process exit code, including a
negative value for a signal. `succeeded` means the process returned zero.
Inspect the backend's native scoring artifacts to determine evaluation results.
A launch failure returns 127, or 126 for a permission error, and records a
credential-free error category in `error` and `stderr.log`. Invalid backend
selection, argument types or environment-file syntax raise a configuration
exception. An unreadable environment file raises its ordinary file exception.

The adapter tests run a small Python fixture CLI. They check the actual child
argv, working directory, config preservation, environment priority, exit code
and log files. They also exercise launch failures, shell metacharacters and a
fake Pier package whose native `app` has no module main guard.
