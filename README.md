# OpenCollabExp

[English](#english) | [简体中文](#simplified-chinese)

<a id="english"></a>

## English

OpenCollabExp owns experiment methods, campaign orchestration, DW deployment,
monitoring, provider routing and report presentation. OpenCollab-Eval owns the
evaluation engine and official scoring, while Pier supplies an independently
installed native backend. Experiment configuration selects the backend and
retains its resource, generation and verification settings.

The companion OpenCollab-Eval interface work lives on
`codex/extract-experiment-layer`. OpenCollab-Eval's `main` branch remains
unchanged. Use a separate checkout of that branch for the paired development
installation. The paired development versions are OpenCollab 0.8.x and
OpenCollab-Eval 0.8.x. The registry contains the canonical OC Duo plus the
retained 31 research workflows and review/fix method, with 33 entries available
through `oc-exp methods --json`.

The canonical entry is `duo`, referencing `opencollab.builtin_workflows:duo`.
Its `base` role profile resolves to `single2`. `oc-exp duo` selects that native
workflow, and `oc-exp g22` is its compatibility command name. Retained research
methods remain individually selectable through their explicit references.

The solver presets select existing experiment methods and native adapters.
Their names, resource settings and model options are carried by the experiment
configuration.

| Solver preset | Use |
| --- | --- |
| `g11` | G1.1 validation council cooperation |
| `g1.1` | Alternate name for the G1.1 validation council preset |
| `g20-exp1` | Evidence-carrying repair council experiment |
| `g20-exp2` | Adaptive dual-candidate repair tournament experiment |
| `g11-wired` | G1.1 wiring ablation with complete evidence handoffs |
| `baseTeam` | Deterministic analyst, coder and tester workflow |
| `TeamPro` | Analyst-led reconnaissance with phased coder and tester work |
| `openhands` | External OpenHands solver selected through a command template |
| `claude-code` | Native Claude Code print-mode solver with the chosen runtime and model |

Set the three source paths to your OpenCollab checkout, the companion OCE branch
checkout and this repository. Create the development environment and tool
caches outside those source trees.

```bash
export OC_SOURCE=/path/to/OpenCollab
export OCE_SOURCE=/path/to/oce-experiment-branch
export EXP_SOURCE=/path/to/OpenCollabExp
export EXP_VENV=/path/to/venvs/opencollab-exp
export UV_CACHE_DIR=/path/to/caches/uv
export PIP_CACHE_DIR=/path/to/caches/pip
export RUFF_CACHE_DIR=/path/to/caches/ruff

git -C "$OCE_SOURCE" branch --show-current
python3.12 -m venv "$EXP_VENV"
"$EXP_VENV/bin/python" -m pip install \
  -e "$OC_SOURCE" \
  -e "$OCE_SOURCE[swebench]" \
  -e "$EXP_SOURCE[dev]"

"$EXP_VENV/bin/oc-exp" --help
"$EXP_VENV/bin/oc-exp" methods --json
```

The branch command should show `codex/extract-experiment-layer`. Pier is
installed separately in the Python environment selected for that backend.
The adapter invokes its native `pier.cli.main.app` entry point.

Keep datasets, provider credentials, DW host configuration, runtime job files,
logs, predictions and reports in an explicit experiment workspace. An external
workspace is convenient for deployment. Repository-local `runs/`, `artifacts/`,
`logs/` and `secrets/` are ignored alternatives. Configure the existing DW
runner and proxy commands from this workspace.

The companion OCE `run` command takes a task JSONL as its positional argument.
Model and provider settings can come from a private environment file containing
`OPENCOLLAB_MODEL`, `OPENCOLLAB_PROVIDER`, `OPENCOLLAB_BASE_URL` and
`OPENCOLLAB_API_KEY`. The following example previews the native invocation.

```bash
export EXP_WORKSPACE=/path/to/experiment-workspace

"$EXP_VENV/bin/oc-exp" run \
  --backend oce \
  --python "$EXP_VENV/bin/python" \
  --cwd "$EXP_WORKSPACE" \
  --output "$EXP_WORKSPACE/oce-backend-logs" \
  --env-file "$EXP_WORKSPACE/provider.env" \
  --dry-run \
  -- run "$EXP_WORKSPACE/tasks.jsonl" \
  --workflow opencollab.builtin_workflows:duo --agent-profile base \
  --output "$EXP_WORKSPACE/oce-results"
```

Add native resource or budget flags according to the experiment settings.
The OCE example uses the task position directly. Native OCE `score` runs its
official scoring entry point for existing predictions. A successful backend
process reports its exit status, while evaluation outcomes come from the native
candidate and scoring evidence.

Pier accepts a native job configuration. Keep its task, agent, resource and
scoring settings in that job file and select the installed Pier interpreter.

```bash
export PIER_PYTHON=/path/to/pier-venv/bin/python

"$EXP_VENV/bin/oc-exp" run \
  --backend pier \
  --python "$PIER_PYTHON" \
  --cwd "$EXP_WORKSPACE" \
  --output "$EXP_WORKSPACE/pier-backend-logs" \
  --env-file "$EXP_WORKSPACE/provider.env" \
  --config "$EXP_WORKSPACE/pier-job.json" \
  --dry-run \
  -- run --yes
```

`--dry-run` prints the selected interpreter, native argv and output paths.
Removing that flag executes the selected native backend. stdout and stderr are
appended to the chosen log directory. Native arguments use an argv list, and
provider environment values remain outside the CLI result.

| Command | Responsibility |
| --- | --- |
| `oc-exp methods` | List all 33 callable experiment method references |
| `oc-exp run` | Invoke an OCE or Pier backend with explicit native arguments |
| `oc-exp duo` | Run canonical OC Duo with experiment deployment and independent scoring |
| `oc-exp g22` | Compatibility command name for canonical Duo |
| `oc-exp campaign` | Run campaign scheduling and supervision |
| `oc-exp swe-run` | Run the existing SWE Pro-Lite experiment runner |
| `oc-exp rejudge-queue` | Process the existing rejudgement queue |
| `oc-exp package-runtime` | Prepare a deployable experiment runtime |
| `oc-exp final-report` | Render the experiment's final result presentation |
| `oc-exp proxy` | Run experiment provider proxy tooling |

Use each experiment command's `--help` for its retained options. The existing
candidate isolation, original scoring resources, process identity handling and
credential protections remain part of their implementations.

[Architecture](docs/architecture.md) explains ownership and dependencies.
[Migration](docs/migration.md) maps former OCE experiment entry points to Exp.
[Methods](docs/methods.md) lists the complete workflow registry and presets.
[Backends](docs/backends.md) documents the process adapter and environment file
format.
[SWE Pro-Lite operations](docs/swe-prolite-operations.md) contains the DW setup
and deployment commands.

Development checks use an external environment and scripted or synthetic test
programs. Run Ruff and the tests relevant to the change.

```bash
"$EXP_VENV/bin/ruff" check .
"$EXP_VENV/bin/python" -m pytest -q \
  tests/test_cli.py tests/test_methods.py \
  tests/test_backend_process.py tests/test_backend_config.py
```

<a id="simplified-chinese"></a>

## 简体中文

OpenCollabExp 负责实验方法、批量实验调度、DW 部署、运行监控、供应方转接与结果展示。
OpenCollab-Eval 负责评测引擎与正式评分，Pier 作为独立安装的原生后端接入。
实验配置选择具体后端，并保留原生资源、生成与验证设置。

配套 OCE 接口修改位于 `codex/extract-experiment-layer` 分支，OCE 的 `main` 分支保持原状。
开发时使用该分支的独立 checkout，与 OpenCollab 和 OpenCollabExp 进行三仓 editable 安装。
配套开发版本为 OpenCollab 0.8.x 和 OpenCollab-Eval 0.8.x。
独立 venv、uv 缓存、pip 缓存和 Ruff 缓存均放在源码目录外，安装命令见上方英文说明。
Pier 安装在所选的独立 Python 环境中，适配器调用其原生 `pier.cli.main.app`。

canonical OC Duo 与保留的 31 个研究工作流、review/fix 方法共 33 项，通过 `oc-exp methods --json` 查看。
canonical 入口为 `duo`，引用 `opencollab.builtin_workflows:duo`，角色 profile `base` 解析到 `single2`。
`oc-exp duo` 选择该原生工作流，`oc-exp g22` 是兼容命令名称。保留的研究方法继续通过显式引用独立选择。
通用 `oc-exp run` 选择 OCE 或 Pier。Duo、campaign、SWE runner、重判队列、运行包、最终报告和
proxy 命令由 Exp 提供，原有候选隔离、正式评分资源、进程身份和凭据保护随实现保留。

solver preset 选择现有实验方法或原生适配器，资源设置与模型选项由实验配置保存。

| Solver preset | 用途 |
| --- | --- |
| `g11` | G1.1 验证委员会协作 |
| `g1.1` | G1.1 验证委员会 preset 的另一个名称 |
| `g20-exp1` | 携带执行证据的修复委员会实验 |
| `g20-exp2` | 自适应双候选修复竞赛实验 |
| `g11-wired` | 带完整证据交接的 G1.1 接线消融实验 |
| `baseTeam` | 按确定流程协作的 analyst、coder 和 tester |
| `TeamPro` | analyst 组织信息收集，coder 与 tester 分阶段执行 |
| `openhands` | 通过命令模板选择外部 OpenHands 求解器 |
| `claude-code` | 使用所选运行包与模型的原生 Claude Code print-mode 求解器 |

| 命令 | 职责 |
| --- | --- |
| `oc-exp methods` | 列出全部 33 项可调用实验方法引用 |
| `oc-exp run` | 使用显式原生参数调用 OCE 或 Pier 后端 |
| `oc-exp duo` | 运行 canonical OC Duo，配合实验部署与独立评分 |
| `oc-exp g22` | canonical Duo 的兼容命令名称 |
| `oc-exp campaign` | 执行批量实验调度与监控 |
| `oc-exp swe-run` | 执行现有 SWE Pro-Lite 实验 runner |
| `oc-exp rejudge-queue` | 处理现有重判队列 |
| `oc-exp package-runtime` | 准备可部署的实验运行包 |
| `oc-exp final-report` | 展示实验最终结果 |
| `oc-exp proxy` | 执行实验供应方转接工具 |

数据集、私密配置、DW 主机配置、job 文件、日志、候选和报告放在显式实验 workspace。
可选择源码目录外的 workspace，也可以使用 Git 已忽略的 `runs/`、`artifacts/`、`logs/` 和 `secrets/`。
模型与供应方配置通过本地环境文件载入。

OCE 原生运行命令采用 `run TASKS_JSONL`，题目文件作为位置参数，方法通过 `--workflow` 传入完整函数引用。
Pier 采用 job 配置文件，外层 `--config` 指定该文件，分隔符之后传入 `run --yes`。
上方示例使用 `--dry-run` 展示实际 argv 和产物路径，去掉该参数后执行所选后端。
原生生成、验证与资源参数由该次实验配置决定。后端返回进程退出码，成绩依据原生候选与评分记录判断。

详细说明可通过 [架构](docs/architecture.md)、[迁移](docs/migration.md)、
[方法清单](docs/methods.zh-CN.md) 和 [后端接口](docs/backends.md) 阅读。
DW 环境准备和部署命令见 [SWE Pro-Lite 操作说明](docs/zh-CN/swe-prolite-operations.md)。
开发检查使用外部 venv，CLI 与后端测试采用假程序，方法测试加载完整 33 项入口并检查实际调用关系。
