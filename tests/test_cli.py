from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

from opencollab_exp import cli


@pytest.mark.parametrize(
    "backend,expected_prefix,native_args",
    [
        ("oce", ["-m", "opencollab_eval"], ["run", "tasks.jsonl", "--concurrency", "2"]),
        ("pier", ["-c", "from pier.cli.main import app; app()"], ["run", "--yes"]),
    ],
)
def test_backend_dry_run_preserves_native_arguments_without_launching(
    tmp_path, capsys, monkeypatch, backend, expected_prefix, native_args
):
    def unexpected_process(*args, **kwargs):
        pytest.fail("dry-run launched a backend")

    monkeypatch.setattr("opencollab_exp.backends.process.subprocess.run", unexpected_process)
    arguments = [
        "run",
        "--backend",
        backend,
        "--python",
        "/opt/selected/bin/python",
        "--cwd",
        str(tmp_path),
        "--output",
        "logs",
        "--env-file",
        "private.env",
        "--dry-run",
    ]
    if backend == "pier":
        arguments.extend(["--config", "job.json"])

    assert cli.main([*arguments, "--", *native_args]) == 0

    plan = json.loads(capsys.readouterr().out)
    expected = ["/opt/selected/bin/python", *expected_prefix, *native_args]
    if backend == "pier":
        expected.extend(["--config", str(tmp_path / "job.json")])
    assert plan["argv"] == expected
    assert plan["cwd"] == str(tmp_path) and plan["artifact_dir"] == str(tmp_path / "logs")
    assert plan["model_calls"] == 0
    assert not (tmp_path / "logs").exists()


@pytest.mark.parametrize("exit_code", [0, 17])
def test_run_serializes_fake_child_status_and_log_paths(tmp_path, capsys, exit_code):
    fixture = tmp_path / "cli_backend_fixture.py"
    fixture.write_text(
        "import json, os, sys\n"
        "print(json.dumps({'argv':sys.argv[1:], 'cwd':os.getcwd(), "
        "'credential_received':os.environ.get('PROVIDER_TOKEN') == 'fake-private-token'}))\n"
        "print('native diagnostic', file=sys.stderr)\n"
        f"sys.exit({exit_code})\n"
    )
    (tmp_path / "provider.env").write_text("PROVIDER_TOKEN=fake-private-token\n")
    arguments = [
        "run",
        "--backend",
        "oce",
        "--python",
        sys.executable,
        "--module",
        fixture.stem,
        "--cwd",
        str(tmp_path),
        "--output",
        "backend-logs",
        "--env-file",
        "provider.env",
        "--",
        "run",
        "tasks.jsonl",
        "--max-tokens",
        "12345",
        "--timeout",
        "90",
    ]

    assert cli.main(arguments) == exit_code

    printed = capsys.readouterr()
    result = json.loads(printed.out)
    assert result["backend"] == "oce" and result["returncode"] == exit_code
    assert result["stdout_path"] == str(tmp_path / "backend-logs/stdout.log")
    assert result["stderr_path"] == str(tmp_path / "backend-logs/stderr.log")
    child = json.loads(Path(result["stdout_path"]).read_text())
    assert child["argv"] == ["run", "tasks.jsonl", "--max-tokens", "12345", "--timeout", "90"]
    assert child["cwd"] == str(tmp_path) and child["credential_received"] is True
    assert Path(result["stderr_path"]).read_text() == "native diagnostic\n"
    assert "fake-private-token" not in printed.out + printed.err


def test_run_reports_invalid_env_file_without_printing_its_value(tmp_path, capsys):
    (tmp_path / "provider.env").write_text("INVALID-NAME=fake-private-token\n")

    result = cli.main(
        [
            "run",
            "--backend",
            "pier",
            "--cwd",
            str(tmp_path),
            "--output",
            "logs",
            "--env-file",
            "provider.env",
            "--",
            "run",
            "--yes",
        ]
    )

    captured = capsys.readouterr()
    assert result == 2 and "line 1" in captured.err
    assert "fake-private-token" not in captured.out + captured.err
    assert not (tmp_path / "logs").exists()


@pytest.mark.parametrize("credential_args", [["--api-key", "fake-private-key"], ["--api-key=fake-private-key"]])
def test_dry_run_hides_explicit_native_api_credentials(tmp_path, capsys, credential_args):
    assert (
        cli.main(
            [
                "run",
                "--backend",
                "oce",
                "--cwd",
                str(tmp_path),
                "--output",
                "logs",
                "--dry-run",
                "--",
                "run",
                "tasks.jsonl",
                *credential_args,
            ]
        )
        == 0
    )

    captured = capsys.readouterr()
    plan = json.loads(captured.out)
    assert plan["backend"] == "oce"
    assert "fake-private-key" not in captured.out + captured.err


def test_run_passes_inline_native_credentials_unchanged_to_the_child(tmp_path, capsys):
    fixture = tmp_path / "credential_cli_fixture.py"
    fixture.write_text(
        "import json, sys\nprint(json.dumps({'received':sys.argv[-2:] == ['--api-key','fake-private-key']}))\n"
    )

    assert (
        cli.main(
            [
                "run",
                "--backend",
                "oce",
                "--python",
                sys.executable,
                "--module",
                fixture.stem,
                "--cwd",
                str(tmp_path),
                "--output",
                "logs",
                "--",
                "run",
                "tasks.jsonl",
                "--api-key",
                "fake-private-key",
            ]
        )
        == 0
    )

    printed = capsys.readouterr()
    result = json.loads(printed.out)
    assert json.loads(Path(result["stdout_path"]).read_text())["received"] is True
    assert "fake-private-key" not in printed.out + printed.err


@pytest.mark.parametrize(
    "name,module",
    [
        ("campaign", "opencollab_exp.commands.swe_g11_parallel_runner"),
        ("swe-run", "opencollab_exp.commands.swe_v1_prolite_runner"),
        ("rejudge-queue", "opencollab_exp.commands.swe_rejudge_queue"),
        ("package-runtime", "opencollab_exp.commands.package_runtime"),
        ("final-report", "opencollab_exp.commands.swe_final_report"),
        ("proxy", "opencollab_exp.commands.llm_api_proxy"),
    ],
)
def test_experiment_command_dispatch_preserves_arguments_and_restores_sys_argv(monkeypatch, name, module):
    original = sys.argv
    observed = []

    def fake_module(selected, run_name):
        observed.append((selected, run_name, sys.argv.copy()))
        raise SystemExit(7)

    monkeypatch.setattr(cli.runpy, "run_module", fake_module)

    assert cli.main([name, "--config", "experiment config.json", "--workers", "3"]) == 7
    assert observed == [(module, "__main__", [module, "--config", "experiment config.json", "--workers", "3"])]
    assert sys.argv is original


def test_g22_dispatch_calls_the_already_imported_native_main(monkeypatch):
    import opencollab_exp.commands as commands

    original = sys.argv
    observed = []
    module = ModuleType("opencollab_exp.commands.g22")

    def native_main(arguments):
        observed.append(arguments)
        return 7

    module.main = native_main
    monkeypatch.setitem(sys.modules, module.__name__, module)
    monkeypatch.setattr(commands, "g22", module, raising=False)

    assert cli.main(["g22", "--config", "experiment config.json", "--workers", "3"]) == 7
    assert observed == [["--config", "experiment config.json", "--workers", "3"]]
    assert sys.argv is original


@pytest.mark.parametrize("exit_value,expected", [(None, 0), ("native configuration error", 1)])
def test_native_system_exit_values_are_handled(monkeypatch, capsys, exit_value, expected):
    def fake_module(*args, **kwargs):
        raise SystemExit(exit_value)

    monkeypatch.setattr(cli.runpy, "run_module", fake_module)

    assert cli.main(["campaign", "--help"]) == expected
    captured = capsys.readouterr()
    assert captured.err == ("native configuration error\n" if expected else "")


def test_methods_command_lists_and_loads_all_33_methods(capsys):
    from opencollab_exp import methods

    assert cli.main(["methods", "--json"]) == 0

    listed = json.loads(capsys.readouterr().out)
    assert len(listed) == 33
    assert listed == methods.WORKFLOW_METHODS
    for name, reference in listed.items():
        selected = methods.load_workflow(reference)
        assert callable(selected) and inspect.iscoroutinefunction(selected), name
