"""Invoke native OCE or Pier CLIs with caller-owned configuration and artifacts."""

from __future__ import annotations

import os
import re
import shlex
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

BackendName = Literal["oce", "pier"]
_MODULES = {"oce": "opencollab_eval", "pier": "pier.cli.main"}
_PIER_ENTRYPOINT = "from pier.cli.main import app; app()"
_ENV_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


@dataclass(frozen=True)
class BackendConfig:
    """Choose a native backend and provide its invocation without changing policy."""

    backend: BackendName
    python: str
    cwd: Path
    artifact_dir: Path
    argv: Sequence[str]
    config: Path | None = None
    module: str | None = None
    env_file: Path | None = None
    env: Mapping[str, str] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        if self.backend not in _MODULES:
            raise ValueError("backend must be oce or pier")
        if not isinstance(self.python, str) or not self.python:
            raise ValueError("python must be an explicit interpreter")
        if self.module is not None and (
            not isinstance(self.module, str) or not self.module
        ):
            raise ValueError("module must be a nonempty Python module name")
        if isinstance(self.argv, (str, bytes)) or any(
            not isinstance(arg, str) for arg in self.argv
        ):
            raise TypeError("argv must be a sequence of strings")
        if any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in self.env.items()
        ):
            raise TypeError("environment names and values must be strings")
        cwd = Path(self.cwd).expanduser().resolve()
        object.__setattr__(self, "cwd", cwd)
        object.__setattr__(self, "argv", tuple(self.argv))
        object.__setattr__(self, "env", dict(self.env))
        for name in ("artifact_dir", "config", "env_file"):
            value = getattr(self, name)
            if value is not None:
                path = Path(value).expanduser()
                object.__setattr__(
                    self, name, path if path.is_absolute() else cwd / path
                )


@dataclass(frozen=True)
class BackendResult:
    """Preserve the process status and locations of native stdout and stderr."""

    backend: BackendName
    returncode: int
    stdout_path: Path
    stderr_path: Path
    error: str | None = None

    @property
    def succeeded(self) -> bool:
        return self.returncode == 0 and self.error is None


def build_argv(config: BackendConfig) -> list[str]:
    """Build the native argv list using exactly the caller's backend arguments."""
    if config.backend == "pier" and config.module is None:
        argv = [config.python, "-c", _PIER_ENTRYPOINT, *config.argv]
    else:
        argv = [
            config.python,
            "-m",
            config.module or _MODULES[config.backend],
            *config.argv,
        ]
    if config.config is not None:
        argv.extend(["--config", str(config.config)])
    return argv


def _env_values(path: Path) -> dict[str, str]:
    values = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        name, separator, raw = line.partition("=")
        name, raw = name.strip(), raw.strip()
        if not separator or _ENV_NAME.fullmatch(name) is None:
            raise ValueError(f"invalid environment assignment at line {number}")
        if raw.startswith(("'", '"')):
            try:
                tokens = shlex.split(raw, comments=True, posix=True)
            except ValueError:
                raise ValueError(
                    f"invalid quoted environment value at line {number}"
                ) from None
            if len(tokens) != 1:
                raise ValueError(f"invalid quoted environment value at line {number}")
            value = tokens[0]
        else:
            value = re.split(r"\s+#", raw, maxsplit=1)[0].rstrip()
        values[name] = value
    return values


def run_backend(config: BackendConfig) -> BackendResult:
    """Run one native invocation and append its streams to caller-owned log files."""
    environment = dict(os.environ)
    if config.env_file is not None:
        environment.update(_env_values(config.env_file))
    environment.update(config.env)
    config.artifact_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = config.artifact_dir / "stdout.log"
    stderr_path = config.artifact_dir / "stderr.log"
    with stdout_path.open("ab") as stdout, stderr_path.open("ab") as stderr:
        try:
            completed = subprocess.run(
                build_argv(config),
                cwd=config.cwd,
                env=environment,
                stdout=stdout,
                stderr=stderr,
                shell=False,
                check=False,
            )
        except OSError as error:
            message = (
                f"Could not launch {config.backend} backend ({type(error).__name__})"
            )
            stderr.write((message + "\n").encode("utf-8"))
            return BackendResult(
                config.backend,
                126 if isinstance(error, PermissionError) else 127,
                stdout_path,
                stderr_path,
                message,
            )
    return BackendResult(config.backend, completed.returncode, stdout_path, stderr_path)
