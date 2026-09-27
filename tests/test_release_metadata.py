"""Packaged experiment workflow guides describe the paired public runtime."""

from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "src" / "opencollab_exp"


def test_packaged_workflow_guides_match_the_08_runtime_boundary() -> None:
    package_readme = _PACKAGE_ROOT / "workflows" / "README.md"
    package_readme_zh = _PACKAGE_ROOT / "workflows" / "README.zh-CN.md"

    for path in (package_readme, package_readme_zh):
        text = path.read_text(encoding="utf-8")
        assert "OpenCollab 0.8.0" in text
        assert "OpenCollab 0.4" not in text
