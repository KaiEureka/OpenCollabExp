"""Experiment workflow references and solver presets consumed by Exp commands."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from opencollab_eval.engine.solver_backend import WorkflowSolverSpec

_MODEL_RUNTIME_OPTIONS = (
    ("--model-name", "OPENCOLLAB_SWE_MODEL_NAME"),
    ("--llm-model", "OPENCOLLAB_SWE_LLM_MODEL"),
)


KIMI_CODING_BASE_URL = "https://api.kimi.com/coding/v1"


SUPPORTED_KIMI_G11_MODELS = frozenset({"k3", "kimi-for-coding"})


def is_kimi_direct_model(model: str) -> bool:
    """Return whether a model has a validated direct Kimi G11 profile."""
    return model.strip() in SUPPORTED_KIMI_G11_MODELS


def kimi_response_model_matches(requested: str, actual: object) -> bool:
    """Match a Kimi response identity without accepting nearby model names."""
    requested_model = requested.strip().lower()
    actual_model = str(actual or "").strip().lower()
    if requested_model == "k3":
        return actual_model == "k3"
    if requested_model == "kimi-for-coding":
        return actual_model in {"kimi-for-coding", "kimi-k2.7"} or actual_model.startswith(("kimi-k2.7-", "kimi-k2.7_"))
    return False


DEFAULT_WORKFLOW_SOLVERS: dict[str, WorkflowSolverSpec] = {
    "g11": WorkflowSolverSpec(
        name="g11",
        workflow_name="validation-council-solve",
        description="G1.1 validation council cooperation strategy.",
        max_attempts=3,
        required_runtime_options=_MODEL_RUNTIME_OPTIONS,
    ),
    "g1.1": WorkflowSolverSpec(
        name="g1.1",
        workflow_name="validation-council-solve",
        description="G1.1 validation council cooperation strategy.",
        max_attempts=3,
        required_runtime_options=_MODEL_RUNTIME_OPTIONS,
    ),
    "g20-exp1": WorkflowSolverSpec(
        name="g20-exp1",
        workflow_name="evidence-action-council-v1",
        description="Experimental evidence-carrying repair council.",
        max_attempts=1,
        default_budget_tokens=1_600_000,
        required_runtime_options=_MODEL_RUNTIME_OPTIONS,
    ),
    "g20-exp2": WorkflowSolverSpec(
        name="g20-exp2",
        workflow_name="candidate-tournament-council-v1",
        description="Adaptive dual-candidate repair tournament.",
        max_attempts=1,
        default_budget_tokens=1_600_000,
        required_runtime_options=_MODEL_RUNTIME_OPTIONS,
    ),
    "g11-wired": WorkflowSolverSpec(
        name="g11-wired",
        workflow_name="validation-council-wired-v1",
        description="G1.1 wiring ablation with complete evidence handoffs.",
        max_attempts=3,
        required_runtime_options=_MODEL_RUNTIME_OPTIONS,
    ),
    "baseTeam": WorkflowSolverSpec(
        name="baseTeam",
        workflow_name="base-team",
        description="Analyst, coder, and tester as a deterministic workflow.",
        max_attempts=1,
        required_runtime_options=_MODEL_RUNTIME_OPTIONS,
    ),
    "TeamPro": WorkflowSolverSpec(
        name="TeamPro",
        workflow_name="team-pro",
        description="Dynamic analyst-led reconnaissance and phased coder/tester workflow.",
        max_attempts=3,
        default_budget_tokens=4_000_000,
        required_runtime_options=_MODEL_RUNTIME_OPTIONS,
        config_overrides={
            "temperature": 1.0,
            "top_p": 1.0,
            "max_output_tokens": 32_768,
        },
    ),
    "openhands": WorkflowSolverSpec(
        name="openhands",
        workflow_name="openhands-external",
        description="External OpenHands solver invoked by a configured command template.",
        max_attempts=2,
        default_budget_tokens=16_000_000,
        required_runtime_options=_MODEL_RUNTIME_OPTIONS,
        config_overrides={
            "temperature": 1.0,
            "top_p": 1.0,
            "max_output_tokens": 32_768,
        },
        args={
            "openhands_command": (
                '"$OPENCOLLAB_REMOTE_REPO/src/opencollab_exp/resources/run_openhands_cli.sh" '
                "--headless --json --override-with-envs --file {prompt_file}"
            ),
            "max_steps": 120,
            "openhands_empty_patch_rejections": 2,
            "max_empty_patch_retries": 1,
            "max_eval_attempts": 2,
        },
    ),
    "claude-code": WorkflowSolverSpec(
        name="claude-code",
        workflow_name="openhands-external",
        description="Claude Code in print mode with a configured runtime and model.",
        max_attempts=1,
        required_runtime_options=_MODEL_RUNTIME_OPTIONS,
        config_overrides={"context_window": 200_000},
        args={
            "llm_provider": "anthropic",
            "openhands_command": (
                '"$OPENCOLLAB_REMOTE_REPO/src/opencollab_exp/resources/'
                'run_claude_code_cli.sh" {container_id} {prompt_file} {output_dir}'
            ),
            "openhands_empty_patch_rejections": 0,
            "max_empty_patch_retries": 0,
            "max_eval_attempts": 1,
            "runner_attempts": 1,
        },
    ),
}


def workflow_solver_spec(name: str) -> WorkflowSolverSpec:
    return DEFAULT_WORKFLOW_SOLVERS[name]


CANONICAL_WORKFLOW_METHODS = {"duo": "opencollab.builtin_workflows:duo"}


WORKFLOW_METHODS: dict[str, str] = {
    **CANONICAL_WORKFLOW_METHODS,
    "analyst-solve": "opencollab_exp.workflows.analyst_solve:analyst_solve",
    "base-team": "opencollab_exp.workflows.base_team:base_team",
    "base-team-single-pass-v1": "opencollab_exp.workflows.base_team_single_pass:base_team_single_pass_v1",
    "candidate-tournament-council-v1": (
        "opencollab_exp.workflows.candidate_tournament_council:"
        "candidate_tournament_council_v1"
    ),
    "evidence-action-council-v1": "opencollab_exp.workflows.evidence_action_council:evidence_action_council_v1",
    "evidence-critic-repair-v1": "opencollab_exp.workflows.evidence_critic_repair:evidence_critic_repair_v1",
    "generate_review_fix": "opencollab_exp.workflows.review_fix:generate_review_fix",
    "scout-solve": "opencollab_exp.workflows.scout_solve:scout_solve",
    "self-collab": "opencollab_exp.workflows.self_collab:self_collab",
    "split-solve": "opencollab_exp.workflows.split_solve:split_solve",
    "swe-committee-v2": "opencollab_exp.workflows.swe_committee_v2:swe_committee_v2",
    "team-pro": "opencollab_exp.workflows.analyst_solve:team_pro",
    "validation-council-dual-coder-contract-v1": (
        "opencollab_exp.workflows.validation_council_dual_coder_contract:"
        "validation_council_dual_coder_contract_v1"
    ),
    "validation-council-dual-coder-selection-v2": (
        "opencollab_exp.workflows.validation_council_dual_coder_selection:"
        "validation_council_dual_coder_selection_v2"
    ),
    "validation-council-dual-coder-selection-v3": (
        "opencollab_exp.workflows.validation_council_dual_coder_selection_files:"
        "validation_council_dual_coder_selection_v3"
    ),
    "validation-council-g20-coder-contract-v1": (
        "opencollab_exp.workflows.validation_council_g20_coder_contract:"
        "validation_council_g20_coder_contract_v1"
    ),
    "validation-council-g20-coder-red-green-v1": (
        "opencollab_exp.workflows.validation_council_g20_coder_red_green:"
        "validation_council_g20_coder_red_green_v1"
    ),
    "validation-council-g20-coder-red-green-v2": (
        "opencollab_exp.workflows.validation_council_g20_coder_red_green_v2:"
        "validation_council_g20_coder_red_green_v2"
    ),
    "validation-council-g20-coder-safe-v1": (
        "opencollab_exp.workflows.validation_council_g20_coder_safe:"
        "validation_council_g20_coder_safe_v1"
    ),
    "validation-council-lean-official-v1": (
        "opencollab_exp.workflows.validation_council_lean_official:"
        "validation_council_lean_official_v1"
    ),
    "validation-council-solve": "opencollab_exp.workflows.validation_council_solve:validation_council_solve",
    "validation-council-triple-coder-contract-v1": (
        "opencollab_exp.workflows.validation_council_triple_coder_contract:"
        "validation_council_triple_coder_contract_v1"
    ),
    "validation-council-wired-coder-heavy-v1": (
        "opencollab_exp.workflows.validation_council_wiring_ablation:"
        "validation_council_wired_coder_heavy_v1"
    ),
    "validation-council-wired-conditional-repair-v1": (
        "opencollab_exp.workflows.validation_council_wiring_ablation:"
        "validation_council_wired_conditional_repair_v1"
    ),
    "validation-council-wired-diagnose-repair-v1": (
        "opencollab_exp.workflows.validation_council_wiring_ablation:"
        "validation_council_wired_diagnose_repair_v1"
    ),
    "validation-council-wired-dual-contract-v1": (
        "opencollab_exp.workflows.validation_council_wired_dual_contract:"
        "validation_council_wired_dual_contract_v1"
    ),
    "validation-council-wired-dual-g20-v1": (
        "opencollab_exp.workflows.validation_council_wired_dual_g20:"
        "validation_council_wired_dual_g20_v1"
    ),
    "validation-council-wired-plus-v1": (
        "opencollab_exp.workflows.validation_council_wiring_ablation:"
        "validation_council_wired_plus_v1"
    ),
    "validation-council-wired-red-rescue-v1": (
        "opencollab_exp.workflows.validation_council_wired_red_rescue:"
        "validation_council_wired_red_rescue_v1"
    ),
    "validation-council-wired-resilient-v1": (
        "opencollab_exp.workflows.validation_council_wiring_ablation:"
        "validation_council_wired_resilient_v1"
    ),
    "validation-council-wired-tournament-v1": (
        "opencollab_exp.workflows.validation_council_wired_tournament:"
        "validation_council_wired_tournament_v1"
    ),
    "validation-council-wired-v1": (
        "opencollab_exp.workflows.validation_council_wiring_ablation:"
        "validation_council_wired_v1"
    ),
}


LEGACY_RESEARCH_WORKFLOWS = tuple(name for name in WORKFLOW_METHODS if name not in CANONICAL_WORKFLOW_METHODS)


LEGACY_BUNDLED_WORKFLOWS = (
    "analyst-solve",
    "base-team",
    "base-team-single-pass-v1",
    "scout-solve",
    "self-collab",
    "split-solve",
    "swe-committee-v2",
    "team-pro",
    "validation-council-dual-coder-contract-v1",
    "validation-council-dual-coder-selection-v2",
    "validation-council-dual-coder-selection-v3",
    "validation-council-lean-official-v1",
    "validation-council-solve",
    "validation-council-triple-coder-contract-v1",
)


def workflow_reference(name_or_reference: str) -> str:
    """Resolve an experiment method or retain an explicit injected reference."""
    if ":" in name_or_reference:
        return name_or_reference
    name = name_or_reference
    if name in DEFAULT_WORKFLOW_SOLVERS:
        name = DEFAULT_WORKFLOW_SOLVERS[name].workflow_name
    try:
        return WORKFLOW_METHODS[name]
    except KeyError as exc:
        raise ValueError(f"unknown experiment workflow {name_or_reference!r}") from exc


def load_workflow(name_or_reference: str) -> Callable[..., Any]:
    """Load the selected method through the evaluation package's generic loader."""
    from opencollab_eval.workflow_loader import load_workflow as load_reference

    return load_reference(workflow_reference(name_or_reference))


def workflow_options(name_or_reference: str) -> dict[str, str]:
    """Provide the explicit generator arguments for one selected method."""
    reference = workflow_reference(name_or_reference)
    label = next((name for name, value in WORKFLOW_METHODS.items() if value == reference), None)
    if label is None:
        label = reference.split(":", 1)[1]
    environment = {
        "validation-council-solve": "shared",
        "validation-council-lean-official-v1": "lean",
    }.get(label, "isolated")
    return {
        "workflow": reference,
        "workflow_label": label,
        "candidate_environment": environment,
    }


def bundled_workflow_registry() -> dict[str, Callable[..., Any]]:
    """Return every supported experiment method, including retained variants."""
    return {name: load_workflow(reference) for name, reference in WORKFLOW_METHODS.items()}


__all__ = [
    "CANONICAL_WORKFLOW_METHODS",
    "LEGACY_RESEARCH_WORKFLOWS",
    "DEFAULT_WORKFLOW_SOLVERS",
    "KIMI_CODING_BASE_URL",
    "LEGACY_BUNDLED_WORKFLOWS",
    "SUPPORTED_KIMI_G11_MODELS",
    "WORKFLOW_METHODS",
    "WorkflowSolverSpec",
    "bundled_workflow_registry",
    "is_kimi_direct_model",
    "kimi_response_model_matches",
    "load_workflow",
    "workflow_options",
    "workflow_reference",
    "workflow_solver_spec",
]
