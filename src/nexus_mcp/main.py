"""Main entry point for the Nexus-MCP server."""

from __future__ import annotations

import logging
import sys

from nexus_mcp.config import load_settings, require_auth_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("nexus_mcp")


def main() -> None:
    logger.info("Initializing Nexus-MCP server...")
    
    # 1. Cargar la configuración desde el entorno (.env)
    settings = load_settings()
    
    # 2. Validar que la autenticación esté configurada (Fail Closed)
    try:
        require_auth_settings(settings)
    except RuntimeError as e:
        logger.error("Configuration error: %s", e)
        sys.exit(1)

    logger.info("Configuration loaded successfully. Host: %s, Port: %s", settings.host, settings.port)
    logger.info("Public URL configured: %s", settings.public_url)

    # Aquí inicializaremos la ejecución del servidor MCP con Streamable HTTP en los siguientes pasos.
    logger.info("Nexus-MCP server skeleton ready for transport integration.")


if __name__ == "__main__":
    main()