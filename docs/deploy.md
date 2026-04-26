# Deploy de SalesCat

Guía paso a paso para desplegar el sistema completo:

- **Backend** + **Postgres** + **Redis** en Railway.
- **Frontend** en Vercel.

Tiempo estimado: 30 minutos la primera vez, 5 minutos para cada redeploy posterior.

## Pre-requisitos

- Cuenta en https://railway.app (free tier alcanza para empezar; cuando se acabe el crédito mensual hay que pasar a paid).
- Cuenta en https://vercel.com (free tier sobra para este proyecto).
- Acceso de administrador al repo de GitHub.
- API key de Groq válida (https://console.groq.com/keys).

## 1. Backend en Railway

### 1.1. Crear proyecto y servicios

1. https://railway.app/new → "Empty Project". Nombre: `salescat`.
2. En el dashboard del proyecto, click **"+ New"** → **"Database"** → **"Add PostgreSQL"**. Railway provisiona la DB automáticamente. Copiar el nombre del servicio (default: `Postgres`).
3. **"+ New"** → **"Database"** → **"Add Redis"**. Default: `Redis`.
4. **"+ New"** → **"GitHub Repo"** → seleccionar el repo `AutoCategorization`. Railway crea un servicio para el código. Renombrarlo a `salescat-api` (Settings → Service Name).

### 1.2. Configurar el servicio backend

En el servicio `salescat-api`:

**Settings → Source**:
- Root Directory: `backend`
- Watch Paths: `backend/**`
- Branch: `main`

Railway detectará el `Dockerfile` y el `railway.json` que están dentro de `backend/`. El `railway.json` configura:
- **Pre-deploy command**: `alembic upgrade head && python -m app.cli.seed` (corre en un container efímero antes del deploy real, idempotente).
- **Healthcheck**: path `/health`, timeout 60s.
- El **start command** NO está en `railway.json` — Railway usa el `CMD` del Dockerfile (`sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips '*'"`). Ver "Gotchas" más abajo para por qué.

**Settings → Config-as-code → Railway Config File**: dejar vacío o `railway.json` (sin slash, relativo al Root Directory). Si pone `/backend/pyproject.toml` o cualquier otra cosa, el deploy falla.

**Settings → Deploy → Custom Start Command**: **DEJAR VACÍO**. Si pones algo acá, override el CMD del Dockerfile y volvés a tener el problema de `$PORT` literal.

**Settings → Networking**:
- Click **"Generate Domain"**. Railway crea una URL pública tipo `salescat-api-production.up.railway.app`. Anotala — la vas a necesitar para Vercel.

### 1.3. Variables de entorno

En **Variables → New Variable** agregar las siguientes:

| Nombre | Valor |
|---|---|
| `SALESCAT_ENVIRONMENT` | `production` |
| `SALESCAT_LOG_LEVEL` | `INFO` |
| `SALESCAT_DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (referencia a la DB del paso 1.1) |
| `SALESCAT_REDIS_URL` | `${{Redis.REDIS_URL}}` (referencia al Redis) |
| `SALESCAT_LLM_PROVIDER` | `groq` |
| `SALESCAT_LLM_MODEL` | `llama-3.3-70b-versatile` |
| `SALESCAT_LLM_API_KEY` | tu API key de Groq |
| `SALESCAT_API_KEY` | random fuerte (ver abajo) |
| `SALESCAT_CORS_ORIGINS` | dejar vacío por ahora — la actualizamos en el paso 3 |

Para generar la `SALESCAT_API_KEY`:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copiala y pegala como valor de la variable. **Guardala también en otro lado** — la vas a necesitar para hacer login al frontend de producción.

> **Nota sobre `${{Postgres.DATABASE_URL}}`**: Railway expone esa sintaxis para referenciar variables de otros servicios. Cuando despliegues, Railway resuelve la URL real (que incluye host privado interno y credenciales). El backend convierte automáticamente `postgresql://` → `postgresql+asyncpg://` para soportar SQLAlchemy async (transformación en `app/core/config.py`).

### 1.4. Disparar el primer deploy

1. Click **"Deploy"** en el servicio (o esperar el auto-deploy si la rama tiene cambios).
2. Mirar los logs en **Deployments → click en el último build**:
   - `pip install -e ".[dev]"` (~1 min)
   - `alembic upgrade head` (crea tablas + enums)
   - `python -m app.cli.seed` (inserta los 5 sellers)
   - `uvicorn ...` arranca, `INFO: Application startup complete`.

### 1.5. Smoke test del backend

Desde tu terminal:

```bash
# Healthcheck público (no requiere key)
curl https://salescat-api-production.up.railway.app/health
# Esperado: {"status":"ok"}

# Endpoint protegido — sin key debe dar 401
curl https://salescat-api-production.up.railway.app/api/v1/sellers
# Esperado: HTTP 401 + {"detail":"API key inválida o ausente"}

# Con key correcta debe dar 200
curl https://salescat-api-production.up.railway.app/api/v1/sellers \
  -H "X-API-Key: <tu-SALESCAT_API_KEY>"
# Esperado: [{"id":1,"name":"Boa"},...]
```

Si todo OK, el backend está listo.

## 2. Frontend en Vercel

### 2.1. Crear proyecto

1. https://vercel.com/new → **"Import Git Repository"** → seleccionar `AutoCategorization`.
2. **Configure Project**:
   - **Framework Preset**: Vite (Vercel lo detecta solo).
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build` (default).
   - **Output Directory**: `dist` (default).
   - **Install Command**: `npm install` (default).

### 2.2. Variables de entorno

En **Environment Variables**:

| Nombre | Valor |
|---|---|
| `VITE_API_URL` | `https://salescat-api-production.up.railway.app` (la URL del paso 1.2) |

> **Importante**: `VITE_*` son las únicas variables que Vite expone al bundle. Cualquier otro prefijo se ignora.

### 2.3. Deploy

Click **"Deploy"**. Vercel buildea el frontend (~30s) y publica.

Una vez deployado, Vercel da una URL tipo `salescat-<random>.vercel.app`. Anotala.

### 2.4. Smoke test del frontend

Abrir la URL de Vercel en el browser:

1. Te redirige a `/login`.
2. Pegar la `SALESCAT_API_KEY` que generaste en el paso 1.3.
3. Click **"Entrar"**.
4. **Esperado**: error de CORS (porque el backend aún no tiene el dominio de Vercel autorizado).

Eso lo arreglamos en el paso 3.

## 3. Cerrar el círculo: CORS

Volver a Railway → servicio `salescat-api` → **Variables**:

- Editar `SALESCAT_CORS_ORIGINS` → setear a `https://<tu-dominio-vercel>.vercel.app`. Si tienes varios (preview deploys de Vercel), separarlos por coma.

Railway redeploya automáticamente al guardar la variable.

Volver al frontend de Vercel, recargar (Ctrl+F5), pegar la API key de nuevo. Ahora **debe entrar** y mostrar el dashboard con los KPIs.

## 4. Verificación end-to-end

Probar el flujo completo:

1. **Dashboard** → KPIs deberían mostrar todo en 0 (DB de prod está vacía excepto los 5 sellers seedeados).
2. **Carga CSV** → arrastrar `vambe_clients.csv` (de la raíz del repo) → "Cargar". Debe insertar 60 filas.
3. **"Categorizar reuniones nuevas"** → arranca un job. El polling debería actualizar el progreso. En Groq free tier puede tardar varias rondas por TPM rate limit (mismo issue que en dev — re-ejecutar el batch desde el dashboard.
4. **Clientes** → tabla con los 60. Click en una fila → drawer con detalle, transcript, categorización.
5. **Re-categorizar** desde el drawer → llamada al LLM, refresca la cat.

## 5. Próximos pasos (opcional)

- **Dominio custom**: Vercel permite mapear un dominio propio en Settings → Domains.
- **HTTPS en Railway**: ya viene por default con la URL `*.up.railway.app`.
- **Logs**: Railway → Logs en tiempo real. Vercel → Deployments → ver build logs.
- **Rate limit**: para mitigar el rate-limit de Groq en producción, considerar pasar a Groq paid o agregar provider Anthropic como fallback (ver backlog §8).
- **Backup de Postgres**: Railway hace backups automáticos en planes paid; en free tier conviene exportar manual periódicamente con `pg_dump`.

## Troubleshooting

### El backend no arranca, alembic falla con "connection refused"

`SALESCAT_DATABASE_URL` no está bien apuntada al servicio Postgres. Verificar que la variable use la sintaxis `${{Postgres.DATABASE_URL}}` (con doble llave). En la pestaña "Variables" debe verse el valor resuelto cuando hovereás sobre la pill.

### "API key inválida o ausente" después de pegar la key correcta

- Verificar que estés usando la URL de Railway en `VITE_API_URL` (sin slash final).
- Verificar que la `SALESCAT_API_KEY` en Railway sea exactamente la que pegaste en el frontend (sin espacios extra).
- Borrar localStorage y volver a pegar.

### CORS bloqueado

- Verificar que `SALESCAT_CORS_ORIGINS` incluya el dominio EXACTO de Vercel (con `https://`, sin `/` al final).
- Si usás preview deploys (`https://salescat-git-feature-x.vercel.app`), agregalos también con coma.

### Healthcheck timeout — "1/1 replicas never became healthy"

Si los logs de deploy muestran que `alembic` arranca pero el container muere antes de que uvicorn levante, o uvicorn loggea `Error: Invalid value for '--port': '$PORT' is not a valid integer`, son alguno de estos casos:

1. **`Custom Start Command` en la UI tiene algo seteado** → override el CMD del Dockerfile. Borralo (dejalo vacío) en Settings → Deploy.
2. **`startCommand` en `railway.json`** → override igual que el de la UI. Para servicios Dockerfile, Railway corre el `startCommand` en *exec form* (sin shell), entonces `$PORT` queda literal y uvicorn truena. Solución: NO setear `startCommand` en `railway.json` para Dockerfile builds — dejá que el `CMD` del Dockerfile (que tiene `["sh", "-c", ...]`) maneje la expansión.
3. **`alembic` y `seed` en el `startCommand`** chained con `&&` → si alguno cuelga (especialmente `engine.dispose()` de asyncpg), uvicorn nunca arranca y el healthcheck timeout. Solución: moverlos a `preDeployCommand` (corre en container efímero, separado del start del servicio).

### Config-as-code apunta al archivo equivocado

Si Railway loggea `config file railway.json does not exist` pero el archivo SÍ está en el repo: revisá Settings → Config-as-code → Railway Config File. Debe ser **vacío** (auto-detect) o `railway.json` (relativo al Root Directory). NO `/backend/railway.json`, NO `/backend/pyproject.toml`. Si el path está roto, Railway falls back a Railpack y se rompe el build del Dockerfile.
