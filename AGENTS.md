# AGENTS.md

OpenCollabExp owns experiment methods, campaigns, deployment, monitoring, and
report presentation. It depends on OpenCollab-Eval and Pier through explicit
interfaces. Evaluation engines must not depend on this package.

Public code, comments, tests, and canonical documentation use English. Chinese
translations live beside their English sources. Git messages and PR text use
Chinese with an English Conventional Commit type.

Retain existing candidate isolation, original scoring resources, evidence,
process identity checks, and credential protections. Model calls and benchmark
runs require an explicit task request. Tests use mocks or synthetic programs.

Keep runtime data, credentials, model transcripts, and experiment outputs out
of Git. Use an explicit workspace outside source trees or ignored run folders.
Use an external virtual environment and external tool caches for development.
Run Ruff and relevant tests before committing. Do not add hashes, frozen
contracts, baselines, or gates without a concrete failure need.
