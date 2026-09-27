"""Experiment methods retain their callable identity and evaluation arguments."""

from __future__ import annotations

import importlib
import inspect
import pkgutil

import pytest
from opencollab_eval.engine.solver_backend import WorkflowSolverSpec

from opencollab_exp import methods, workflows


def test_every_declared_workflow_has_an_explicit_loadable_method():
    declared = set()
    for item in pkgutil.iter_modules(workflows.__path__):
        module = importlib.import_module(f"{workflows.__name__}.{item.name}")
        for value in vars(module).values():
            if inspect.isfunction(value) and value.__module__ == module.__name__:
                spec = getattr(value, "__workflow_spec__", None)
                if spec is not None:
                    declared.add(spec.name)
    assert set(methods.WORKFLOW_METHODS) == declared | {"generate_review_fix"} | set(methods.CANONICAL_WORKFLOW_METHODS)
    for name in declared:
        selected = methods.load_workflow(name)
        assert selected.__workflow_spec__.name == name
        assert inspect.iscoroutinefunction(selected)


def test_original_package_exports_keep_the_same_method_functions():
    original_names = set()
    for export in workflows.__all__:
        selected = getattr(workflows, export)
        name = selected.__workflow_spec__.name
        if name in methods.CANONICAL_WORKFLOW_METHODS:
            continue
        original_names.add(name)
        assert methods.load_workflow(name) is selected
    assert original_names == set(methods.LEGACY_BUNDLED_WORKFLOWS)


@pytest.mark.parametrize("solver", ["g20-exp1", "g20-exp2", "g11-wired"])
def test_previously_missing_solver_targets_resolve_to_their_actual_methods(solver):
    preset = methods.workflow_solver_spec(solver)
    assert isinstance(preset, WorkflowSolverSpec)
    selected = methods.load_workflow(solver)
    assert selected.__workflow_spec__.name == preset.workflow_name
    assert methods.workflow_reference(solver) == methods.WORKFLOW_METHODS[preset.workflow_name]


@pytest.mark.parametrize(
    ("name", "expected_environment"),
    [
        ("duo", "isolated"),
        ("validation-council-solve", "shared"),
        ("validation-council-lean-official-v1", "lean"),
        ("validation-council-dual-coder-contract-v1", "isolated"),
        ("validation-council-dual-coder-selection-v2", "isolated"),
        ("generate_review_fix", "isolated"),
    ],
)
def test_named_and_explicit_methods_carry_the_same_generator_arguments(name, expected_environment):
    expected = {
        "workflow": methods.WORKFLOW_METHODS[name],
        "workflow_label": name,
        "candidate_environment": expected_environment,
    }
    assert methods.workflow_options(name) == expected
    assert methods.workflow_options(expected["workflow"]) == expected


def test_explicit_external_module_reference_uses_the_generic_loader():
    reference = "opencollab_exp.workflows.review_fix:generate_review_fix"
    module = importlib.import_module("opencollab_exp.workflows.review_fix")
    assert methods.workflow_reference(reference) == reference
    assert methods.load_workflow(reference) is module.generate_review_fix


def test_unknown_named_method_fails_before_generator_execution():
    with pytest.raises(ValueError, match="unknown experiment workflow"):
        methods.workflow_options("missing-experiment-method")


@pytest.mark.parametrize("solver", ["openhands", "claude-code"])
def test_external_solver_presets_keep_shared_candidate_route_and_exp_resources(solver):
    preset = methods.workflow_solver_spec(solver)
    assert preset.workflow_name == "openhands-external"
    assert "src/opencollab_exp/resources/" in preset.args["openhands_command"]
