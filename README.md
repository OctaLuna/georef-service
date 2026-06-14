# Kaa Iya — Microservicio GeoRef (FastAPI)

Microservicio interno de **georreferenciación** para la plataforma Kaa Iya. Resuelve un par de
coordenadas WGS84 (lat/lng) al **departamento** y **provincia** boliviana correspondiente
mediante *point-in-polygon* sobre datos GADM. Lo consume el backend NestJS al registrar
proyectos con coordenadas.

## Stack

| Componente | Tecnología |
|---|---|
| Framework | FastAPI 0.118 (Starlette 0.48) |
| Servidor | Gunicorn 23 + Uvicorn workers |
| Geoespacial | GeoPandas 1.1 + Shapely 2.0 |
| Config | Pydantic Settings (desde `.env`) |
| Datos | GADM 4.1 Bolivia nivel 2 (`data/bolivia.geojson`, ~1.1 MB, **no versionado**) |
| Python | 3.11+ (probado en 3.12) |

## Inicio rápido

```bash
cd georef-service
cp .env.example .env

# Crear entorno virtual e instalar dependencias
python -m venv venv
# Windows:
venv\Scripts\pip install -r requirements.txt
# Linux/macOS:
# venv/bin/pip install -r requirements.txt

# Descargar el GeoJSON de GADM (~1.1 MB)
bash scripts/download_data.sh        # o: make data

# Arrancar en desarrollo (hot-reload)
venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
# o, en Linux/macOS:  make dev
```

Verificar:

```bash
curl http://127.0.0.1:8001/geo/health
# {"status":"ok","environment":"development","features_loaded":112,"geojson_path":"data/bolivia.geojson"}
```

> En Windows el venv usa `venv\Scripts\`; en Linux/macOS usa `venv/bin/`. El `Makefile`
> asume rutas de Windows para `install`; en Linux ajusta a `venv/bin/`.

## Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `ENVIRONMENT` | `development` | `development` \| `production`. En `production` se deshabilitan `/docs`, `/redoc`, `/openapi.json` |
| `HOST` | `127.0.0.1` | Host de escucha (uvicorn dev) |
| `PORT` | `8001` | Puerto |
| `GEOJSON_PATH` | `data/bolivia.geojson` | Ruta al GeoJSON GADM |
| `ALLOWED_ORIGINS` | `["http://127.0.0.1:3000","http://localhost:3000"]` | Lista blanca CORS (JSON array). Ajustar al origen del backend |

## Endpoints

### `GET /geo/health`
Estado del servicio y número de features cargadas.

```json
{ "status": "ok", "environment": "development", "features_loaded": 112, "geojson_path": "data/bolivia.geojson" }
```

### `POST /geo/pip`  — Point-in-Polygon
Resuelve coordenadas a departamento/provincia. Valida que estén dentro del bounding box de
Bolivia (lat `-23..-9`, lng `-70..-57`); fuera de rango → `422`.

```bash
curl -X POST http://127.0.0.1:8001/geo/pip \
  -H "Content-Type: application/json" \
  -d '{"lat": -17.7833, "lng": -63.1821}'
```
```json
{ "found": true, "lat": -17.7833, "lng": -63.1821, "department": "Santa Cruz", "municipality": "Andrés Ibáñez", "country": "Bolivia" }
```

> **Nota:** GADM nivel 2 devuelve la **provincia** (112 unidades), no el municipio exacto
> (339). El campo `municipality` contiene el nombre de la provincia. Para municipios exactos
> se requeriría `gadm41_BOL_3.json` (nivel 3).

## Datos geoespaciales

- Fuente: GADM 4.1 Bolivia nivel 2 (`https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_BOL_2.json`).
- `data/bolivia.geojson` **no se versiona** (gitignored); descargar con `scripts/download_data.sh`.
- Se carga en memoria al iniciar (≈120 MB de RAM por proceso padre).

## Por qué `--preload` (Gunicorn)

`gunicorn.conf.py` usa `preload_app = True`: el `GeoDataFrame` se carga **una vez** en el proceso
padre y los workers lo comparten por *copy-on-write*, en lugar de cargar ~120 MB por worker.
Con 9 workers el consumo total ronda ~300 MB en lugar de >1 GB.

## Integración con el backend

El backend NestJS llama a `POST {GEOREF_URL}/geo/pip`. **Este servicio no debe exponerse a
internet** sin control de acceso: en local escucha en `127.0.0.1`; en PaaS debe desplegarse
como *servicio privado* / interno y referenciarse desde el backend por su URL interna
(`GEOREF_URL`). Si GeoRef no responde, el backend degrada elegantemente (`georefFailed=true`),
no falla el registro. Ver `../docs/kaaiya-georef-integration-guide.md`.

## Tests

```bash
venv\Scripts\pytest tests/ -v          # o: make test
venv\Scripts\pytest tests/ --cov=app   # con cobertura
```
Suite actual: 12 casos (ciudades conocidas, validación de rango, health).

## Comandos del Makefile

| Comando | Acción |
|---|---|
| `make install` | Crea venv e instala dependencias (rutas Windows) |
| `make data` | Descarga `bolivia.geojson` |
| `make dev` | Uvicorn con `--reload` en `127.0.0.1:8001` |
| `make prod` | Gunicorn con `gunicorn.conf.py` |
| `make test` | pytest |

## Despliegue

Ver la guía de Render/Railway en la raíz del monorepo: `../DEPLOY.md`. En PaaS, Gunicorn debe
escuchar en `0.0.0.0:$PORT` (la plataforma inyecta `$PORT`); sobreescribir el `bind` de
`gunicorn.conf.py` vía variable de entorno o flag de arranque.

## Troubleshooting

| Problema | Solución |
|---|---|
| `features_loaded: 0` | Falta `data/bolivia.geojson`; ejecutar `scripts/download_data.sh` |
| `422` en `/geo/pip` | Coordenadas fuera del bounding box de Bolivia (esperado) |
| Alto consumo de RAM | Verificar `preload_app=True`; reducir `workers` en `gunicorn.conf.py` |
| El backend marca `georefFailed` | GeoRef caído o inalcanzable desde `GEOREF_URL` |
