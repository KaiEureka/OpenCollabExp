"""Retained dual-coder execution for historical selector experiments."""

from __future__ import annotations

from typing import Any

from opencollab.workflows import CandidateRun
from opencollab_eval.patch_diff import patch_paths

from . import validation_council_wired_dual_contract as contract
from . import validation_council_wired_dual_g20 as dual
from ._public_api import toolset
from ._validation_council_solve_defs import (
    SHARED_RULES,
    _complete_goal,
    coder_role_timeout_seconds,
    structured_role_timeout_seconds,
)
from .validation_council_dual_coder_contract import (
    CONTRACT_PROMPT,
    CROSS_COMPONENT_CODER_PROMPT,
    MINIMAL_CODER_PROMPT,
)

TOTAL_RUNNER_BUDGET = None





def _coder_tools() -> list[Any]:
    return toolset("bash", "file_read", "file_write", "apply_patch", "grep", "git_diff")


async def _coder_candidate(
    ctx: Any,
    *,
    label: str,
    prompt: str,
    goal: str,
    shared_command: str = "",
) -> CandidateRun:
    tools = _coder_tools()
    raw = await ctx.candidate_agent(
        prompt.format(
            rules=SHARED_RULES,
            goal=goal,
            public_command=shared_command or "(no shared public command)",
        ),
        label=label,
        tools=tools,
        budget=None,
        timeout=coder_role_timeout_seconds(),
    )
    records = [
        dual._public_record(record)
        for record in raw.test_records
        if isinstance(record, dict)
    ]
    observed_command = str(records[0].get("command") or "").strip() if records else shared_command
    return CandidateRun(
        label=raw.label,
        output={
            "coder_output": raw.output,
            "public_command": observed_command,
            "public_test_records": records,
        },
        diff=raw.diff,
        test_records=raw.test_records,
        verified_targets=raw.verified_targets,
    )


async def _contract_adjudicate(
    ctx: Any,
    *,
    goal: str,
    candidate_a: CandidateRun,
    candidate_b: CandidateRun,
    selector_prompt: str = CONTRACT_PROMPT,
) -> tuple[str, Any, str]:
    evidence, paths, truncated = contract._judge_input(candidate_a, candidate_b)
    if truncated:
        return "A", None, "contract-evidence-incomplete-default-a"
    try:
        result = await ctx.agent(
            selector_prompt.format(
                rules=SHARED_RULES,
                goal=goal,
                candidates=evidence,
            ),
            schema=contract.CONTRACT_SCHEMA,
            label="dual-coder-contract-adjudicator",
            tools=[],
            budget=None,
            timeout=structured_role_timeout_seconds(),
        )
    except Exception as exc:  # noqa: BLE001
        await ctx.log(f"dual coder contract adjudicator unavailable after {type(exc).__name__}")
        result = None
    winner = contract._validated_judge_winner(result, paths)
    if winner is None:
        return "A", result, "contract-evidence-insufficient-default-a"
    return winner, result, "contract-adjudicated"




async def _run_dual_coder_contract(
    ctx: Any,
    args: dict[str, Any],
    *,
    selector_prompt: str,
    adjudicator: Any = None,
) -> dict[str, Any]:
    """Run the existing candidate and selection sequence with a per-call prompt."""
    goal = _complete_goal(str(args.get("goal") or args.get("description") or ""))
    if not goal:
        return {"status": "error", "error": 'missing "goal" or "description"'}

    source_before = await ctx.diff()

    await ctx.phase("dual-coder-a")
    candidate_a = await _coder_candidate(
        ctx,
        label="dual-coder-contract-a",
        prompt=MINIMAL_CODER_PROMPT,
        goal=goal,
    )
    shared_command = dual._candidate_command(candidate_a)

    await ctx.phase("dual-coder-b")
    candidate_b = await _coder_candidate(
        ctx,
        label="dual-coder-contract-b",
        prompt=CROSS_COMPONENT_CODER_PROMPT,
        goal=goal,
        shared_command=shared_command,
    )

    await ctx.phase("dual-coder-mechanical-selection")
    winner, reason, needs_judge = contract._mechanical_choice(
        candidate_a,
        candidate_b,
    )
    judge_result: Any = None
    if needs_judge:
        await ctx.phase("dual-coder-contract-adjudication")
        choose = adjudicator if adjudicator is not None else _contract_adjudicate
        winner, judge_result, reason = await choose(
            ctx,
            goal=goal,
            candidate_a=candidate_a,
            candidate_b=candidate_b,
            selector_prompt=selector_prompt,
        )

    source_before_adoption = await ctx.diff()
    if source_before_adoption != source_before:
        raise RuntimeError("candidate_workspace_tracking_failure: source worktree changed before candidate adoption")

    candidates = {"A": candidate_a, "B": candidate_b}
    preserve_paths = [str(path) for path in args.get("injected_test_paths") or [] if str(path)]
    adopted, adoption_attempts = await dual._adopt(
        ctx,
        winner=winner,
        candidates=candidates,
        preserve_paths=preserve_paths,
    )
    return {
        "status": "done" if adopted is not None else "incomplete",
        "winner": winner,
        "selection_reason": reason,
        "judge_used": needs_judge,
        "judge_result": judge_result,
        "adopted": adopted,
        "adoption_attempts": adoption_attempts,
        "shared_public_command": shared_command,
        "candidates": {
            "A": {
                "kind": "minimal-root-cause-coder",
                "nonempty": bool(candidate_a.diff.strip()),
                "diff_bytes": len(candidate_a.diff.encode("utf-8")),
                "changed_paths": patch_paths(candidate_a.diff),
                "public_command": dual._candidate_command(candidate_a),
                "public_test_records": dual._candidate_records(candidate_a),
            },
            "B": {
                "kind": "cross-component-contract-coder",
                "nonempty": bool(candidate_b.diff.strip()),
                "diff_bytes": len(candidate_b.diff.encode("utf-8")),
                "changed_paths": patch_paths(candidate_b.diff),
                "public_command": dual._candidate_command(candidate_b),
                "public_test_records": dual._candidate_records(candidate_b),
            },
        },
        "tokens_spent": ctx.tokens_spent(),
    }


