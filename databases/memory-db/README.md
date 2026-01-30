# Memory DB – EI-UNP IA

Base PostgreSQL utilizada para persistir usuarios, sesiones y mensajes compartidos entre todos los agentes del ecosistema EI-UNP IA. Cada registro de sesión y mensaje queda asociado a un usuario y se almacena con UUIDs generados por `uuid-ossp`.

## Inicialización
Ejecutar el contenedor desde `databases/memory-db/`:

```bash
docker compose up -d
```

El `docker-compose.yml` monta `./initdb` en `/docker-entrypoint-initdb.d/`, por lo que los scripts se aplican automáticamente:
- `01_extensions.sql` habilita `uuid-ossp`.
- `02_schema.sql` crea las tablas `eco_mcp_memoria_usuario`, `eco_mcp_memoria_sesion`, `eco_mcp_memoria_mensaje` y el índice `idx_eco_sesion_app`.

## Configuración
- Puerto reservado del pool EI-UNP IA: `14013`.
- Variables de entorno definidas en `docker-compose.yml` (`POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`). Ajustar los valores mediante un `.env` externo si se requiere, evitando versionar secretos.
