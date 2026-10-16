"""Smoke test: comprueba que el paquete se importa y pytest funciona."""

import nexus_mcp


def test_package_imports_and_has_version():
    assert nexus_mcp.__version__ == "0.0.1"