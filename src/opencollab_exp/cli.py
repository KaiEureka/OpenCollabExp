"""Experiment deployment CLI over independent evaluation backends."""
from __future__ import annotations

import argparse
import importlib
import json
import runpy
import sys
from dataclasses import asdict
from pathlib import Path

from opencollab_exp import __version__

COMMAND_MODULES = {
    'g22': 'opencollab_exp.commands.g22',
    'campaign': 'opencollab_exp.commands.swe_g11_parallel_runner',
    'swe-run': 'opencollab_exp.commands.swe_v1_prolite_runner',
    'rejudge-queue': 'opencollab_exp.commands.swe_rejudge_queue',
    'package-runtime': 'opencollab_exp.commands.package_runtime',
    'final-report': 'opencollab_exp.commands.swe_final_report',
    'proxy': 'opencollab_exp.commands.llm_api_proxy',
}


def _module_main(module: str, arguments: list[str]) -> int:
    original = sys.argv
    try:
        sys.argv = [module, *arguments]
        try:
            runpy.run_module(module, run_name='__main__')
        except SystemExit as exc:
            if exc.code is None:
                return 0
            if isinstance(exc.code, int):
                return exc.code
            print(str(exc.code), file=sys.stderr)
            return 1
        return 0
    finally:
        sys.argv = original


def _display_argv(argv: list[str]) -> list[str]:
    """Redact credential options in a command preview without changing execution."""
    secret_options = {"--api-key", "--token", "--auth-token", "--password", "--access-token"}
    shown = []
    redact_next = False
    for value in argv:
        if redact_next:
            shown.append("[redacted]")
            redact_next = False
        elif value in secret_options:
            shown.append(value)
            redact_next = True
        elif value.partition("=")[0] in secret_options and "=" in value:
            shown.append(value.partition("=")[0] + "=[redacted]")
        else:
            shown.append(value)
    return shown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='oc-exp', description=__doc__)
    parser.add_argument('--version', action='version', version=__version__)
    subs = parser.add_subparsers(dest='command', required=True)
    methods = subs.add_parser('methods', help='List experiment workflow entry points')
    methods.add_argument('--json', action='store_true')
    backend = subs.add_parser('run', help='Invoke an OCE or Pier backend with explicit arguments')
    backend.add_argument('--backend', choices=['oce', 'pier'], required=True)
    backend.add_argument('--python', default=sys.executable)
    backend.add_argument('--cwd', type=Path, required=True)
    backend.add_argument('--output', type=Path, required=True, help='Experiment artifact directory')
    backend.add_argument('--config', type=Path, help='Native backend job configuration')
    backend.add_argument('--env-file', type=Path, help='Private environment file for the child process')
    backend.add_argument('--module', help='Explicit alternate backend module')
    backend.add_argument('--dry-run', action='store_true')
    backend.add_argument('backend_args', nargs=argparse.REMAINDER, help='Native CLI arguments after --')
    for name in COMMAND_MODULES:
        subs.add_parser(name, add_help=False, help=f'Run experiment {name} tooling')
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments and arguments[0] in COMMAND_MODULES:
        if arguments[0] == 'g22':
            return importlib.import_module(COMMAND_MODULES['g22']).main(arguments[1:])
        return _module_main(COMMAND_MODULES[arguments[0]], arguments[1:])
    parser = build_parser()
    args = parser.parse_args(arguments)
    if args.command == 'methods':
        from opencollab_exp.methods import WORKFLOW_METHODS
        if args.json:
            print(json.dumps(WORKFLOW_METHODS, indent=2, ensure_ascii=False))
        else:
            for name, reference in sorted(WORKFLOW_METHODS.items()):
                print(f'{name}\t{reference}')
        return 0
    if args.command == 'run':
        from opencollab_exp.backends import BackendConfig, build_argv, run_backend
        remainder = args.backend_args[1:] if args.backend_args[:1] == ['--'] else args.backend_args
        config = BackendConfig(
            backend=args.backend, python=args.python, cwd=args.cwd, artifact_dir=args.output,
            argv=tuple(remainder), config=args.config, module=args.module, env_file=args.env_file,
        )
        try:
            if args.dry_run:
                print(json.dumps({'backend':args.backend, 'argv':_display_argv(build_argv(config)),
                                  'cwd':str(config.cwd), 'artifact_dir':str(config.artifact_dir),
                                  'model_calls':0}, indent=2))
                return 0
            result = run_backend(config)
        except (OSError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        print(json.dumps(asdict(result), default=str, indent=2))
        return result.returncode if result.returncode is not None else 2
    raise AssertionError(f'unhandled command {args.command}')


if __name__ == '__main__':
    raise SystemExit(main())
