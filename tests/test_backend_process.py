from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

from opencollab_exp.backends import BackendConfig, build_argv, run_backend


@pytest.fixture
def native_cli(tmp_path: Path) -> Path:
    module = tmp_path / "native_backend_fixture.py"
    module.write_text(
        "import json, os, sys\n"
        "from pathlib import Path\n"
        "Path(os.environ['CAPTURE_PATH']).write_text(json.dumps({\n"
        "  'argv': sys.argv[1:], 'cwd': os.getcwd(),\n"
        "  'setting': os.environ.get('BACKEND_SETTING'),\n"
        "  'token_received': os.environ.get('BACKEND_TOKEN') == 'test-private-value',\n"
        "  'literal': os.environ.get('LITERAL_VALUE'),\n"
        "  'empty': os.environ.get('EMPTY_VALUE'),\n"
        "}))\n"
        "print('native output')\n"
        "print('native diagnostic', file=sys.stderr)\n"
        "sys.exit(int(os.environ.get('BACKEND_EXIT', '0')))\n",
        encoding="utf-8",
    )
    return module


@pytest.mark.parametrize("backend,command", [("oce", "duo"), ("pier", "run")])
def test_native_arguments_config_cwd_and_logs_are_forwarded(
    native_cli, tmp_path, backend, command
):
    job = tmp_path / "job with spaces.json"
    original = (
        '{"resources":{"cpus":2},"generation_budget":0,"verification_budget":7}\n'
    )
    job.write_text(original)
    capture = tmp_path / "capture.json"
    arguments = (
        command,
        "--workers",
        "3",
        "--generation-budget",
        "0",
        "--verification-budget",
        "7",
    )
    config = BackendConfig(
        backend=backend,
        python=sys.executable,
        cwd=tmp_path,
        artifact_dir=Path("native logs"),
        argv=arguments,
        config=Path(job.name),
        module=native_cli.stem,
        env={"CAPTURE_PATH": str(capture)},
    )

    result = run_backend(config)

    observed = json.loads(capture.read_text())
    assert observed["argv"] == [*arguments, "--config", str(job)]
    assert observed["cwd"] == str(tmp_path)
    assert job.read_text() == original
    assert result.succeeded and result.returncode == 0
    assert result.stdout_path == tmp_path / "native logs/stdout.log"
    assert result.stderr_path == tmp_path / "native logs/stderr.log"
    assert result.stdout_path.read_text() == "native output\n"
    assert result.stderr_path.read_text() == "native diagnostic\n"


def test_nonzero_native_exit_is_preserved_and_existing_logs_are_appended(
    native_cli, tmp_path
):
    artifacts = tmp_path / "logs"
    artifacts.mkdir()
    (artifacts / "stdout.log").write_text("previous output\n")
    config = BackendConfig(
        "pier",
        sys.executable,
        tmp_path,
        artifacts,
        ("run",),
        module=native_cli.stem,
        env={"CAPTURE_PATH": str(tmp_path / "capture.json"), "BACKEND_EXIT": "17"},
    )

    result = run_backend(config)

    assert result.returncode == 17 and not result.succeeded and result.error is None
    assert result.stdout_path.read_text() == "previous output\nnative output\n"
    assert result.stderr_path.read_text() == "native diagnostic\n"


def test_env_file_is_literal_overridden_and_kept_out_of_logs(
    native_cli, tmp_path, monkeypatch
):
    monkeypatch.setenv("BACKEND_SETTING", "parent")
    marker = tmp_path / "shell-marker"
    env_file = tmp_path / "provider.env"
    env_file.write_text(
        "# Provider settings\n"
        "export BACKEND_SETTING='from file' # comment\n"
        "BACKEND_TOKEN=test-private-value\n"
        f"LITERAL_VALUE=$(touch {marker})\n"
        "EMPTY_VALUE=\n"
    )
    config = BackendConfig(
        "oce",
        sys.executable,
        tmp_path,
        Path("logs"),
        ("duo",),
        module=native_cli.stem,
        env_file=Path(env_file.name),
        env={
            "CAPTURE_PATH": str(tmp_path / "capture.json"),
            "BACKEND_SETTING": "override",
        },
    )

    result = run_backend(config)

    observed = json.loads((tmp_path / "capture.json").read_text())
    assert observed["setting"] == "override" and observed["token_received"] is True
    assert observed["literal"] == f"$(touch {marker})" and not marker.exists()
    assert observed["empty"] == ""
    assert os.environ["BACKEND_SETTING"] == "parent"
    for value in [
        repr(config),
        repr(result),
        result.stdout_path.read_text(),
        result.stderr_path.read_text(),
    ]:
        assert "test-private-value" not in value


def test_missing_interpreter_returns_launch_failure_with_log_paths(tmp_path):
    config = BackendConfig(
        "oce", str(tmp_path / "absent-python"), tmp_path, Path("logs"), ("duo",)
    )

    result = run_backend(config)

    assert result.returncode == 127 and not result.succeeded
    assert result.error == "Could not launch oce backend (FileNotFoundError)"
    assert result.stdout_path.exists()
    assert result.stderr_path.read_text() == result.error + "\n"


def test_argument_metacharacters_are_forwarded_as_one_argument(native_cli, tmp_path):
    marker = tmp_path / "shell-marker"
    argument = f"literal value; touch {marker}"
    config = BackendConfig(
        "pier",
        sys.executable,
        tmp_path,
        Path("logs"),
        ("run", argument),
        module=native_cli.stem,
        env={"CAPTURE_PATH": str(tmp_path / "capture.json")},
    )

    result = run_backend(config)

    assert result.succeeded
    assert json.loads((tmp_path / "capture.json").read_text())["argv"] == [
        "run",
        argument,
    ]
    assert not marker.exists()


@pytest.mark.parametrize(
    "backend,prefix",
    [
        ("oce", ["-m", "opencollab_eval"]),
        ("pier", ["-c", "from pier.cli.main import app; app()"]),
    ],
)
def test_default_native_entrypoint_uses_caller_interpreter(tmp_path, backend, prefix):
    config = BackendConfig(
        backend, "/opt/chosen/bin/python", tmp_path, Path("logs"), ("--help",)
    )

    assert build_argv(config) == ["/opt/chosen/bin/python", *prefix, "--help"]


def test_default_pier_calls_native_app_without_a_module_main_guard(tmp_path):
    package = tmp_path / "pier/cli"
    package.mkdir(parents=True)
    (tmp_path / "pier/__init__.py").write_text("")
    (package / "__init__.py").write_text("")
    (package / "main.py").write_text(
        "import json, os, sys\n"
        "from pathlib import Path\n"
        "def app():\n"
        "    Path(os.environ['CAPTURE_PATH']).write_text(json.dumps(sys.argv[1:]))\n"
        "    print('pier app invoked')\n"
        "    sys.exit(23)\n"
    )
    capture = tmp_path / "pier-args.json"
    config = BackendConfig(
        "pier",
        sys.executable,
        tmp_path,
        Path("logs"),
        ("run", "--n-concurrent-trials", "4"),
        config=Path("job.json"),
        env={"CAPTURE_PATH": str(capture)},
    )

    result = run_backend(config)

    assert result.returncode == 23
    assert json.loads(capture.read_text()) == [
        "run",
        "--n-concurrent-trials",
        "4",
        "--config",
        str(tmp_path / "job.json"),
    ]
    assert result.stdout_path.read_text() == "pier app invoked\n"
