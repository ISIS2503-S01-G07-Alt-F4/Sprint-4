# Usuarios microservice

Microservicio Django responsable de la administración de usuarios y la integración con Auth0.

## Ejecutar con Docker
1. Instala y levanta Docker Desktop.
2. Desde la carpeta `usuarios/` ejecuta `docker compose up --build` la primera vez.
3. Para reinicios posteriores basta con `docker compose up`.

El contenedor aplica migraciones automáticamente y expone la aplicación en `http://localhost:8081`.

### Variables de entorno relevantes
Se consumen desde el archivo `.env` ubicado en la raíz del monorepo.

| Variable | Descripción |
| --- | --- |
| `DJANGO_DB_*` | Configuración de la base de datos Postgres. |
| `AUTHZ_DOMAIN` | Dominio de Auth0 (sin protocolo). |
| `AUTHZ_AUDIENCE` | Audience configurado en Auth0. |
| `CLIENT_ID` / `CLIENT_SECRET` | Credenciales de la aplicación machine-to-machine. |

## APIs para expedición de tokens JWT

| Método/Path | Descripción |
| --- | --- |
| `POST /api/auth/tokens/password/` | Solicita a Auth0 un JWT usando username/password (resource-owner password). Espera `username`, `password` y opcional `audience`. |
| `POST /api/auth/tokens/client-credentials/` | Solicita un token vía client-credentials, opcionalmente con otro `audience`. |
| `GET /api/auth/tokens/session/` | Devuelve el `id_token` almacenado en la sesión del usuario autenticado. |

Estas rutas devuelven directamente la respuesta de Auth0 y se pueden consumir desde otros microservicios sin necesidad de reconstruir el contenedor.