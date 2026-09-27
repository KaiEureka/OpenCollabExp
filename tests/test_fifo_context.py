"""The experiment launcher forwards explicit model context."""

import os
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

import opencollab_exp


@pytest.mark.parametrize("generator", ["single-agent", "workflow"])
def test_fifo_launcher_passes_explicit_context_to_generator(tmp_path, generator):
    binaries = tmp_path / "bin"
    binaries.mkdir()
    python = binaries / "python3"
    python.write_text(
        f'#!/bin/sh\nif [ "$1" = "-" ]; then exec {shlex.quote(sys.executable)} "$@"; fi\n'
        'while [ "$#" -gt 0 ]; do\n  if [ "$1" = "--context-window" ]; then\n'
        '    printf "context=%s\\n" "$2"\n  fi\n  shift\ndone\n'
    )
    python.chmod(0o755)
    instance = tmp_path / "instance.json"
    instance.write_text('{}\n')
    token = tmp_path / "test-input"
    token.write_text('offline-fixture\n')
    script = Path(opencollab_exp.__file__).parent / "resources/run_swe_v2_one_from_fifo.sh"
    environment = dict(os.environ)
    environment.pop("OPENCOLLAB_CONTEXT_WINDOW", None)
    environment.update(
        PATH=f"{binaries}:{environment['PATH']}",
        OPENCOLLAB_REMOTE_ROOT=str(tmp_path), OPENCOLLAB_REMOTE_REPO=str(tmp_path),
        OPENCOLLAB_REMOTE_PROXY_BASE_URL="http://127.0.0.1:1",
        OPENCOLLAB_MODEL="unknown-model", OPENCOLLAB_SWE_GENERATOR=generator,
        OPENCOLLAB_INSTANCE_FILE=str(instance),
        OPENCOLLAB_SWE_WORKFLOW="fixture-workflow",
        OPENCOLLAB_SWE_WORKFLOW_ENTRYPOINT="fixture.workflows:solve",
        OPENCOLLAB_SWE_CANDIDATE_ENVIRONMENT="isolated",
    )
    completed = subprocess.run(
        ["bash", str(script), "task-1", "unused-image", str(token), str(tmp_path / "run"),
         "unknown-model", "", "", "65536", "1048576"],
        env=environment, capture_output=True, text=True, check=True,
    )
    assert "context=1048576" in completed.stdout

