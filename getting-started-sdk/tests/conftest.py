import sys
from pathlib import Path

import pytest

SDK_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SDK_ROOT / "scripts"))


class CallRecorder:
    """Stands in for subprocess.call; returns the queued exit codes, then 0."""

    def __init__(self):
        self.calls: list[dict] = []
        self.returns: list[int] = []

    def __call__(self, cmd, **kwargs):
        self.calls.append({"cmd": list(cmd), **kwargs})
        return self.returns.pop(0) if self.returns else 0

    @property
    def cmds(self) -> list[list[str]]:
        return [c["cmd"] for c in self.calls]


@pytest.fixture
def calls():
    return CallRecorder()


@pytest.fixture(autouse=True)
def isolated_sdks(monkeypatch, tmp_path):
    """Never read or create the real sdks/ folder of the machine running the tests."""
    import target_paths
    monkeypatch.setattr(target_paths, "SDKS_DIR", tmp_path / "sdks")
    monkeypatch.setattr(target_paths, "WSL_SDKS_DIR", tmp_path / "sdks")
    monkeypatch.delenv("UBX_SDKS_DIR", raising=False)
