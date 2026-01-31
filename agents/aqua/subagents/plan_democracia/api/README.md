# AQUA – Plan Democracia API (Contrato v0)

## Endpoints
- `GET /health`: verificación básica.
- `POST /chat`: interfaz principal con Gemini.

## Headers obligatorios / opcionales
| Header           | Requerido | Descripción |
|------------------|-----------|-------------|
| `X-User-Id`      | Sí        | Identificador del usuario solicitante. |
| `X-Session-Id`   | Opcional  | Identificador de sesión. Si no se envía, el servidor genera uno. |
| `GEMINI_API_KEY` | Opcional  | Solo en modo `DEBUG=true`. Si `DEBUG=true` y no se envía, se rechaza la petición. En producción se ignora y se usa la key interna. |

## Body del request
```json
{
  "message": "Texto del analista",
  "input_mode": "text",
  "user": {
    "username": "usuario",
    "nombres": "Nombre completo",
    "dependencia": "Dependencia",
    "grupo": "Grupo",
    "id_busuario": "abc-123",
    "servicios": [
      { "url": "servicio", "rol": "Rol", "id_rol": 111 }
    ]
  }
}
```
- `message`: obligatorio, string no vacío.
- `input_mode`: obligatorio (`text` o `voice`).
- `user`: opcional (se acepta cualquier estructura para compatibilidad con el frontend).

## Respuesta
```json
{
  "outMode": "text",
  "text": "Respuesta en Markdown",
  "attachment": {
    "chartData": {},
    "snippets": {}
  }
}
```
- `outMode`: coincide con `input_mode` o valor por defecto `text`.
- `text`: respuesta generada por Gemini.
- `attachment`: siempre presente, aunque vacío.

El header `X-Session-Id` siempre se devuelve con el valor utilizado (nuevo o reutilizado).

## Ejemplos curl
### 1. Primera solicitud (sin sesión previa, DEBUG=true)
```bash
curl -X POST http://localhost:14001/chat \
  -H "Content-Type: application/json" \
  -H "X-User-Id: user-001" \
  -H "GEMINI_API_KEY: <clave-temporal>" \
  -d '{
    "message": "¿Qué es el Plan Democracia?",
    "input_mode": "text"
  }' -i
```
Revise el header `X-Session-Id` de la respuesta para reutilizarlo.

### 2. Solicitud siguiente reutilizando la sesión
```bash
curl -X POST http://localhost:14001/chat \
  -H "Content-Type: application/json" \
  -H "X-User-Id: user-001" \
  -H "X-Session-Id: <UUID devuelto anteriormente>" \
  -H "GEMINI_API_KEY: <clave-temporal>" \
  -d '{
    "message": "¿Cuáles son los mecanismos de participación?",
    "input_mode": "text"
  }'
```

> Nota: el frontend actual consume otro formato (`content/sources/chart`). Este contrato JSON es el usado para pruebas con Postman/curl y será el puente hacia el frontend definitivo.
