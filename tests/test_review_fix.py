"""Review/fix experiment behavior preserved after moving out of the evaluator."""

from __future__ import annotations

import asyncio
from typing import Any

from opencollab_eval.engine.environment import ExecResult

from opencollab_exp.workflows.review_fix import generate_review_fix


def run(operation):
    return asyncio.run(operation)


class FakeEnv:
    async def exec_cmd(self, command: str, timeout: float = 120.0) -> ExecResult:
        return ExecResult(0, "diff --git a/x b/x\n+fixed\n", "")


class ScriptedCtx:
    def __init__(self, env: Any, replies: list[Any]):
        self.env = env
        self.replies = list(replies)
        self.agent_calls = []
        self.phases = []

    async def phase(self, name):
        self.phases.append(name)

    async def agent(self, prompt, *, schema=None, label=None):
        self.agent_calls.append({"prompt": prompt, "schema": schema, "label": label})
        return self.replies.pop(0)


def test_generate_review_fix_skips_apply_when_ok(tmp_path):
    env = FakeEnv()
    # Stage 1 implement -> text; stage 2 review verdict -> needs_changes False.
    ctx = ScriptedCtx(
        env,
        replies=[
            "implemented the fix",
            {"needs_changes": False, "feedback": "looks good"},
        ],
    )

    result = run(generate_review_fix(ctx, {"description": "fix the bug"}))

    # Only two agent calls — the apply stage was skipped.
    assert len(ctx.agent_calls) == 2
    # The review call used a schema (structured verdict).
    assert ctx.agent_calls[1]["schema"] is not None
    assert result["needs_changes"] is False

def test_generate_review_fix_runs_apply_when_changes_requested(tmp_path):
    env = FakeEnv()
    ctx = ScriptedCtx(
        env,
        replies=[
            "implemented the fix",
            {"needs_changes": True, "feedback": "rename foo to bar"},
            "applied the feedback",
        ],
    )

    result = run(generate_review_fix(ctx, {"description": "fix the bug"}))

    # Three agent calls — implement, review, apply.
    assert len(ctx.agent_calls) == 3
    assert result["needs_changes"] is True
    # The apply-stage prompt carried the review feedback.
    assert "rename foo to bar" in ctx.agent_calls[2]["prompt"]

def test_generate_review_fix_marks_truncated_diff_unavailable(tmp_path):
    class TruncatedReviewEnv(FakeEnv):
        async def exec_cmd(self, cmd: str, timeout: float = 120.0) -> ExecResult:
            return ExecResult(
                returncode=0,
                stdout="diff --git a/x b/x\n+partial secret tail\n",
                stderr="",
                stdout_truncated=True,
                stdout_dropped_bytes=7000,
            )

    ctx = ScriptedCtx(
        TruncatedReviewEnv(),
        replies=[
            "implemented the fix",
            {"needs_changes": False, "feedback": "unavailable"},
        ],
    )

    run(generate_review_fix(ctx, {"description": "fix the bug"}))

    review_prompt = ctx.agent_calls[1]["prompt"]
    assert "diff unavailable" in review_prompt
    assert "stdout dropped 7000 bytes" in review_prompt
    assert "partial secret tail" not in review_prompt
