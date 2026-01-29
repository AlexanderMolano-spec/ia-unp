# Knowledge DB Bootstrap

## Inicialización con Docker
Levanta un contenedor PostgreSQL (15+ recomendado) montando `databases/knowledge-db/initdb/` en `/docker-entrypoint-initdb.d/`. El entrypoint ejecutará los scripts en orden y dejará lista la base `mcp-unp-db` con datos y secuencias sincronizadas.

```bash
docker run --name knowledge-db \
  -e POSTGRES_DB=mcp-unp-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 14010:5432 \
  -v $(pwd)/databases/knowledge-db/initdb:/docker-entrypoint-initdb.d \
  postgres:16
```

## Scripts entregados
1. `01_extensions.sql` instala `vector` y `pg_trgm` antes de crear tablas o índices que dependan de ellas.
2. `02_schema.sql` replica exactamente el DDL del dump (secuencias, tablas, constraints, índices) sin recrear objetos internos de extensiones.
3. `03_data.sql` carga todos los registros del dump original y ejecuta los `SELECT setval(...)` para dejar las secuencias alineadas.

## Preservación del dump original
El archivo original `databases/knowledge-db/knowledge.sql` permanece intacto para auditorías o nuevas migraciones. Los scripts `initdb/` se generaron directamente desde ese dump para evitar inconsistencias y hacer que la inicialización automática en Docker sea reproducible sin errores por extensiones.
