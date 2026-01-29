# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to Semantic Versioning.

## [0.1.0] – 2026-01-29
### Added
- MCP Server base creado con FastMCP.
- Exposición HTTP streamable (SSE) lista para clientes remotos.
- Integración inicial con proxy Nginx para publicar `/mcp` hacia internet.
- Tools generales (`ping`, `get_current_date`) disponibles para validación.
- Flujo `initialize → tools/list → tools/call` verificado vía HTTP externo.
