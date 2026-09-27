"""Canonical OC Duo and retained experiment wrappers use their owning execution bodies."""

from __future__ import annotations

import pytest
from opencollab.builtin_workflows import duo, get_builtin_workflows

from opencollab_exp import methods, workflows
from opencollab_exp.workflows import validation_council_dual_coder_contract as g21


def test_registry_uses_the_single_oc_duo_implementation():
    assert get_builtin_workflows().get("duo").fn is duo
    assert methods.load_workflow("duo") is workflows.duo is duo
    assert methods.workflow_reference("duo") == "opencollab.builtin_workflows:duo"
    assert methods.CANONICAL_WORKFLOW_METHODS == {"duo": "opencollab.builtin_workflows:duo"}
    assert [spec.name for spec in get_builtin_workflows().list_specs()] == ["duo"]


def test_old_g22_variants_are_explicit_research_methods():
    for name in (
        "validation-council-dual-coder-selection-v2",
        "validation-council-dual-coder-selection-v3",
    ):
        assert name in methods.LEGACY_RESEARCH_WORKFLOWS
        assert methods.load_workflow(name).__workflow_spec__.name == name
        assert name not in methods.CANONICAL_WORKFLOW_METHODS
    assert "duo" not in methods.LEGACY_RESEARCH_WORKFLOWS


@pytest.mark.asyncio
async def test_g21_compatibility_entry_passes_its_prompt_to_oc_execution(monkeypatch):
    calls = []
    outcome = {"status": "done", "adopted": "A"}

    async def run(ctx, args, **options):
        calls.append((ctx, args, options))
        return outcome

    monkeypatch.setattr(g21, "run_dual_coder", run)
    context, arguments = object(), {"description": "Repair public behavior"}
    assert await g21.validation_council_dual_coder_contract_v1(context, arguments) is outcome
    assert calls == [(context, arguments, {"selector_prompt": g21.CONTRACT_PROMPT,
        "coder_prompts": (g21.MINIMAL_CODER_PROMPT, g21.CROSS_COMPONENT_CODER_PROMPT),
        "role_rules": g21.SHARED_RULES})]
    assert g21.validation_council_dual_coder_contract_v1.__workflow_spec__.name == (
        "validation-council-dual-coder-contract-v1"
    )
