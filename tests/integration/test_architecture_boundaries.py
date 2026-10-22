from pathlib import Path

import nexus_mcp
from nexus_mcp.authorization.policy import POLICY
from nexus_mcp.gateway import default_tools

SRC = Path(nexus_mcp.__file__).parent


def _imports_tools(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    return "nexus_mcp.tools" in text or "from .tools" in text or "from ..tools" in text


def test_server_does_not_import_tools_directly():
    assert not _imports_tools(SRC / "server.py")


def test_only_the_gateway_imports_tools():
    offenders = []
    for path in SRC.rglob("*.py"):
        relative = path.relative_to(SRC)
        if relative.parts[0] == "tools" or relative.name == "gateway.py":
            continue
        if _imports_tools(path):
            offenders.append(str(relative))
    assert offenders == []


def test_every_policy_tool_has_an_implementation():
    assert set(POLICY) == set(default_tools())

def test_auth_package_does_not_know_authorization_or_tools():
    forbidden = ("nexus_mcp.authorization", "nexus_mcp.tools", "nexus_mcp.gateway",
                 "from ..authorization", "from ..tools", "from ..gateway")
    for path in (SRC / "auth").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert not any(item in text for item in forbidden), path.name