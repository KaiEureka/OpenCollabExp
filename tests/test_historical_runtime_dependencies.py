"""Publication handles historical target dependency declarations."""

from __future__ import annotations

import json

import pytest
from opencollab_eval.engine.swe_test_plan_contract import (
    legacy_javascript_runtime_dependencies,
    previous_javascript_runtime_dependencies,
)
from opencollab_eval.engine.swe_v1_remote_test_plan import prolite_test_plan

from opencollab_exp.commands import swe_final_report_model as final_report_model


@pytest.mark.parametrize(
    "historical_dependencies",
    [previous_javascript_runtime_dependencies, legacy_javascript_runtime_dependencies],
)
def test_final_report_normalizes_only_declared_historical_javascript_dependencies(
    historical_dependencies,
):
    trusted = prolite_test_plan(
        {"repo_language": "javascript", "repo": "nodebb/nodebb"},
        ["test/topics.js | title"],
        target_file="/eval_input/f2p.targets.json",
    )
    historical = json.loads(json.dumps(trusted))
    historical["runtime_dependencies"] = historical_dependencies(trusted["adapter"])

    final_report_model._normalize_historical_runtime_dependencies(historical, trusted)

    assert historical == trusted


def test_final_report_does_not_normalize_unknown_javascript_dependencies():
    trusted = prolite_test_plan(
        {"repo_language": "javascript", "repo": "nodebb/nodebb"},
        ["test/topics.js | title"],
        target_file="/eval_input/f2p.targets.json",
    )
    forged = json.loads(json.dumps(trusted))
    forged["runtime_dependencies"] = [{"root": "answer.json", "required_paths": ["answer.json"]}]

    final_report_model._normalize_historical_runtime_dependencies(forged, trusted)

    assert forged != trusted

