# progress.md — Microservicio GeoRef (Kaa Iya)

Microservicio FastAPI de georreferenciación (point-in-polygon) que resuelve coordenadas WGS84
a departamento/provincia de Bolivia. Lo consume el backend NestJS.

> Repo independiente (pendiente de inicializar git). La documentación vive dentro de
> `georef-service/`. Para la integración con el backend ver
> `../api-rest-amazonia/docs/kaaiya-georef-integration-guide.md`.

---

## Estado base (implementado en sesiones previas)

- App FastAPI (`app/main.py`) con CORS por lista blanca y Swagger deshabilitado en producción
  (`docs_url=None` si `ENVIRONMENT=production`).
- Endpoints (`app/routers/geo.py`):
  - `GET /geo/health` → estado + `features_loaded`.
  - `POST /geo/pip` → resuelve lat/lng a `{found, department, municipality, country}`; valida
    bounding box de Bolivia (lat −23..−9, lng −70..−57) → fuera de rango `422`.
- Servicio geoespacial (`app/services/geo_service.py`): carga el `GeoDataFrame` en import y hace
  point-in-polygon con Shapely; normaliza nombres de departamento/provincia.
- Configuración (`app/config.py`) con Pydantic Settings desde `.env`.
- Datos: GADM 4.1 Bolivia nivel 2 (`data/bolivia.geojson`, ~1.1 MB, **no versionado**;
  `scripts/download_data.sh`). 112 features cargadas.
- Gunicorn (`gunicorn.conf.py`) con `preload_app=True` (workers comparten el GeoDataFrame por
  copy-on-write) y bind `127.0.0.1:8001`.
- Tests: 10–12 casos en `tests/test_geo.py`.

---

## 2026-06-13 — Sesión de remediación de auditoría + preparación de despliegue

### ✅ Qué se implementó / cambió

- **AUDIT-005 — Dependencias actualizadas** (`requirements.txt`) para corregir CVEs de runtime:
  - `fastapi` 0.115.0 → **0.118.0** (arrastra `starlette` 0.38.6 → **0.48.0**, corrige
    CVE-2024-47874 DoS multipart y CVE-2025-54121).
  - `gunicorn` 22.0.0 → **23.0.0** (CVE de request smuggling).
  - `geopandas` 1.0.1 → **1.1.2** (PYSEC-2026-62).
  - `uvicorn` 0.32.0 → 0.32.1 · `python-dotenv` 1.0.1 → **1.2.2** · `pytest` 8.3.3 → 8.3.5 · `httpx` → 0.28.1.
  - Verificado: `pytest` → **12 passed** con las nuevas versiones; `/geo/health` OK (112 features).
- **Documentación:** creado `README.md` del microservicio (stack, quick start Windows/Linux,
  variables de entorno, endpoints con ejemplos, datos GADM, por qué `--preload`, integración
  con el backend, tests, troubleshooting).
- **Despliegue:** documentado en la guía raíz `../DEPLOY.md` cómo subirlo a Render/Railway como
  **servicio privado/interno** (no exponer a internet), con `bind 0.0.0.0:$PORT` (la PaaS inyecta
  `$PORT`) y descarga del GeoJSON en el build.

> Nota: este servicio **no** es repo git todavía, por lo que estos cambios son archivos (sin commit).

### 📊 Estado actual

| Componente | Estado |
|---|---|
| `GET /geo/health` | ✅ 200 (`features_loaded: 112`) |
| `POST /geo/pip` | ✅ Resuelve dept/provincia; `422` fuera de Bolivia |
| Tests (`pytest`) | ✅ 12 passed |
| Dependencias / CVEs runtime | ✅ Actualizadas (starlette/gunicorn/geopandas) |
| Datos `bolivia.geojson` | ✅ Presente en local (~1.1 MB) |
| README | ✅ Creado |
| Local | ✅ `uvicorn` en `127.0.0.1:8001` |
| Veredicto despliegue | 🟢 Listo (como servicio privado en Render/Railway) |

### 🔜 Qué sigue

| Item | Prioridad |
|------|-----------|
| Inicializar repo git propio del microservicio | Alta |
| Para despliegue: usar `gunicorn ... -b 0.0.0.0:$PORT` y descargar GeoJSON en el build | Alta |
| Ampliar cobertura de tests (`pytest --cov=app` ≥80%) | Media |
| CVE residual `starlette` (CVE-2025-62727, fix 0.49.1 requiere fastapi >0.118 aún no estable) | Media |
| GADM nivel 3 (`gadm41_BOL_3.json`, 339 features) para municipio exacto en lugar de provincia | Baja |
| Rate limiting (`slowapi`) si se expone a más clientes internos | Baja |
