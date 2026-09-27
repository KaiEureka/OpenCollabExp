from pathlib import Path

import pytest

from opencollab_exp.backends import BackendConfig, run_backend


def test_backend_selection_and_structured_arguments_are_required(tmp_path):
    with pytest.raises(ValueError, match="backend must be oce or pier"):
        BackendConfig("unknown", "python3", tmp_path, Path("logs"), ())
    with pytest.raises(TypeError, match="sequence of strings"):
        BackendConfig("oce", "python3", tmp_path, Path("logs"), "duo --workers 3")


@pytest.mark.parametrize(
    "assignment", ["BACKEND_TOKEN='private-value", "not-an-env-name=private-value"]
)
def test_invalid_env_file_reports_location_without_its_value(tmp_path, assignment):
    env_file = tmp_path / "provider.env"
    env_file.write_text(assignment + "\n")
    config = BackendConfig(
        "oce", "python3", tmp_path, Path("logs"), (), env_file=env_file
    )

    with pytest.raises(ValueError, match="line 1") as error:
        run_backend(config)

    assert "private-value" not in str(error.value)
    assert not (tmp_path / "logs").exists()
