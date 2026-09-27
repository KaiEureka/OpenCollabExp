"""Standalone Base defaults are independent from workflow role configuration."""

from test_swe_g11_parallel_runner import _args, _load_module


def test_standalone_base_inherits_single2_compatibility_and_explicit_override():
    runner = _load_module()
    inherited = runner.resolve_config(_args(workflow="single-agent"))
    explicit = runner.resolve_config(_args(
        workflow="single-agent",
        workflow_env=["OPENCOLLAB_TRUST_STREAMED_OUTPUT_ON_TERMINAL_MISMATCH=0"],
    ))
    workflow = runner.resolve_config(_args(workflow="duo"))
    assert inherited.agent_profile == "single2"
    assert "OPENCOLLAB_TRUST_STREAMED_OUTPUT_ON_TERMINAL_MISMATCH=1" in inherited.workflow_env
    assert "OPENCOLLAB_TRUST_STREAMED_OUTPUT_ON_TERMINAL_MISMATCH=0" in explicit.workflow_env
    assert "OPENCOLLAB_TRUST_STREAMED_OUTPUT_ON_TERMINAL_MISMATCH=1" not in explicit.workflow_env
    assert workflow.agent_profile is None
    assert not any(value.startswith("OPENCOLLAB_TRUST_STREAMED_OUTPUT_ON_TERMINAL_MISMATCH=")
                   for value in workflow.workflow_env)
