# EI-UNP IA – MCP Server

## Descripción
El servidor MCP del Ecosistema de Información UNP (EI-UNP) actúa como backend cognitivo para los agentes de IA que operan sobre fuentes institucionales. Expone herramientas verificables del dominio general para validar la capa de orquestación y sirve como punto de entrada único para futuros agentes especializados (AQUA, AERIS, IGNIS, TERRA).

## Arquitectura de alto nivel
- Servicio MCP independiente construido con FastMCP.
- Comunicación vía HTTP streamable (Server-Sent Events) para soportar respuestas progresivas.
- Despliegue detrás de un proxy Nginx que publica el endpoint `/mcp` de forma segura a internet (por ejemplo, dominios Tailscale habilitados).

## Requisitos
- Python 3.12+ con soporte para FastMCP.
- FastMCP y dependencias listadas en `mcp/server/requirements.txt`.
- Nginx o proxy equivalente para exponer `/mcp` hacia internet (opcional en entornos cerrados, recomendado para producción).

## Ejecución del servidor MCP
1. Posicionarse en `mcp/server/`.
2. Instalar dependencias si es necesario con `python -m pip install -r requirements.txt`.
3. Ejecutar el servidor HTTP streamable (SSE) escuchando en `0.0.0.0:8000` bajo el path `/mcp`:

```bash
python main.py --host 0.0.0.0 --port 8000 --path /mcp --http-stream
```

El servicio quedará disponible en `https://<dominio>/mcp`, atendiendo sesiones MCP vía SSE.

## Pruebas desde internet (curl)
Todas las llamadas deben incluir los headers `Accept: application/json, text/event-stream` y `mcp-session-id`. Los ejemplos siguientes utilizan un dominio de referencia `https://mcp.ei-unp.net/mcp` que debe reemplazarse por el dominio real expuesto por Nginx.

### initialize
```bash
curl -N https://mcp.ei-unp.net/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: sess-123" \
  -d '{
    "jsonrpc": "2.0",
    "id": "init-1",
    "method": "initialize",
    "params": {
      "protocolVersion": "1.0",
      "capabilities": {
        "prompts": {"listChanged": false},
        "resources": {"subscriptions": false},
        "tools": {"listChanged": false}
      },
      "clientInfo": {"name": "curl", "version": "1.0"}
    }
  }'
```

### tools/call (ping)
```bash
curl -N https://mcp.ei-unp.net/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: sess-123" \
  -d '{
    "jsonrpc": "2.0",
    "id": "ping-1",
    "method": "tools/call",
    "params": {
      "name": "ping",
      "arguments": {}
    }
  }'
```

La misma sesión admite llamadas a `tools/list` y `tools/call` para `get_current_date`, lo que permite verificar el pipeline completo.

## Estado actual
- MCP operativo y expuesto vía HTTP streamable.
- Tools generales (`ping`, `get_current_date`) registradas y funcionando.
- Flujo `initialize → tools/list → tools/call` validado desde internet.
- Base lista para incorporar control de sesiones, migración de tools avanzadas e integración con agentes cognitivos.

## Roadmap / Milestones
**Milestone 1 – MCP Base (COMPLETADO)**
- MCP HTTP streamable
- Proxy
- Tools generales
- Pruebas externas

**Milestone 2 – Gobernanza**
- SessionPayload
- Headers de autoridad
- Roles y permisos

**Milestone 3 – Agentes**
- Integración AQUA, AERIS, IGNIS, TERRA
- Tools específicas por agente

**Milestone 4 – Auditoría y persistencia**
- Registro de llamadas
- Base de datos de auditoría
