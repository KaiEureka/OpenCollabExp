"""Experiment strategies and their guides live in the experiment package."""

from pathlib import Path

import opencollab_exp

_SOURCE = Path(opencollab_exp.__file__).resolve().parent


def test_evaluation_strategy_is_owned_by_eval_package() -> None:
    fact_sheet = (_SOURCE / "workflows" / "_fact_sheet.py").read_text(encoding="utf-8")
    analyst_runtime = (_SOURCE / "workflows" / "_analyst_solve_runtime.py").read_text(
        encoding="utf-8"
    )

    assert "opencollab" not in fact_sheet
    assert "from ._fact_sheet import" in analyst_runtime
    assert "from ._public_api import format_findings_report" in analyst_runtime


def test_workflow_documentation_uses_packaged_layout() -> None:
    readme = (_SOURCE / "workflows" / "README.md").read_text(encoding="utf-8")
    stale_layout_fragments = (
        "swebench/gen_prediction_workflow.py",
        "OPENCOLLAB_WORKFLOWS_DIR",
        "`opencollab workflow",
        "opencollab/.venv",
        "`application/workflow.py`",
        "`opencollab/adapters/tools/`",
        "`workflows/` relative to the working directory",
    )

    assert [fragment for fragment in stale_layout_fragments if fragment in readme] == []

