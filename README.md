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

> Configuración: copiar `mcp/server/.env.example` a `mcp/server/.env`, ajustar credenciales y nunca versionar `.env`.

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

## Milestone: Knowledge DB (Plan Democracia / AQUA)
- Contenedor PostgreSQL con `pgvector` y `pg_trgm` desplegado usando los scripts `databases/knowledge-db/initdb/01_extensions.sql`, `02_schema.sql` y `03_data.sql`.
- Seeds del Plan Democracia (AQUA) cargados automáticamente; la base queda disponible en `databases/knowledge-db/` con el puerto reservado `14010` del pool EI-UNP IA.
- Verificación: `psql -h 127.0.0.1 -p 14010 -U knowledge_db_user -d knowledge_db -c "SELECT count(*) FROM public.eco_aqua_base_conocimiento;"` debería devolver el total de fragmentos registrados.
- MCP Server sigue ejecutándose fuera de Docker (pendiente contenerizar cuando estabilice la integración con las bases).
- Esta Knowledge DB compartida albergará schemas dedicados por agente (`aqua`, `terra`, `ignis`, `aeris`) y se complementará con las futuras Memory, Policy y Auth DB.

## Asignación de puertos (Pool EI-UNP IA)
El ecosistema de IA de la UNP reserva de forma permanente el rango 14000–14019 para su arquitectura contenerizada, evitando colisiones con servicios adyacentes.

| Categoría         | Puerto  | Componente                                                   |
|-------------------|---------|--------------------------------------------------------------|
| Agentes           | 14000   | Agent MASTER                                                 |
|                   | 14001   | Agent AQUA                                                   |
|                   | 14002   | Agent IGNIS                                                  |
|                   | 14003   | Agent AERIS                                                  |
|                   | 14004   | Agent TERRA                                                  |
| Servicios Core    | 14005   | MCP Server (FastMCP, HTTP streamable / SSE)                  |
| Bases de Datos    | 14010   | Knowledge DB (AQUA / Plan Democracia, pgvector)             |
| (PostgreSQL)      | 14011   | Auth DB (Roles y Permisos)                                   |
|                   | 14012   | Policy / Audit DB                                            |
|                   | 14013   | Memory DB (Sesiones, mensajes, memoria persistente)          |
| Reserva           | 14014–19| Crecimiento futuro (gateway, redis interno, UI, nuevos agentes) |

Notas:
- El pool dedicado garantiza que los contenedores de EI-UNP IA no entren en conflicto con otros servicios.
- Las bases de datos permanecen privadas y solo pueden exponerse temporalmente durante validaciones controladas.
- El MCP Server es el único endpoint previsto para exposición pública, siempre a través de un proxy seguro.

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

## Próximo paso
- Conectar el MCP Server a la Knowledge DB mediante el cliente/driver correspondiente.
- Preparar las tools del agente AQUA para operar sobre su schema dedicado (`aqua`).
- Planificar la incorporación de Memory DB, Policy DB y Auth DB como servicios compartidos.
