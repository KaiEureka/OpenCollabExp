"""Controller evaluation-only calls omit generation credentials."""

import inspect

from opencollab_exp.commands import swe_v1_prolite_runner as runner


def test_local_eval_only_skips_generation_dependencies():
    main_source = inspect.getsource(runner.main)
    payload_source = inspect.getsource(runner._controller._remote_payload)
    assert "if args.eval_only:" in main_source
    assert (
        '"token": "" if eval_only or remote_api_env_file else get_proxy_token(args.proxy_env_file)'
        in payload_source
    )

