# EI-UNP Scraper (newspaper3k)

Servicio FastAPI que descarga y normaliza artículos web usando `newspaper3k`. Está pensado como microservicio de apoyo para los agentes IA, centralizando la extracción de `titulo` y `texto` desde un conjunto de URLs.

## Endpoint
- `POST /extract`
  - Body:
    ```json
    {
      "urls": [
        "https://example.org/noticia"
      ],
      "lang": "es",
      "concurrency": 4
    }
    ```
  - Response:
    ```json
    {
      "ok": true,
      "results": [
        {
          "url": "https://example.org/noticia",
          "titulo": "Titular normalizado",
          "texto": "Contenido limpia...",
          "error": null
        }
      ]
    }
    ```

## Puerto expuesto
- Contenedor escucha en `5001`.
- Docker Compose lo publica en `http://localhost:14014`.

## Dependencias principales
- FastAPI + Uvicorn
- newspaper3k
- httpx (futuras extensiones)
- lxml con `html_clean` para sanitización

## Ejecución con Docker Compose
Desde `infra/docker/scraper/`:
```bash
docker compose up -d --build
```
El contenedor `ei-unp-scraper` quedará disponible en `http://localhost:14014/extract`.

## Estado
- Imagen ligera sobre `python:3.11-slim` con dependencias de `newspaper3k` instaladas.
- Listo para consumo por MCP y agentes IA una vez orquestado desde el gateway.
