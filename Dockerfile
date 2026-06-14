FROM python:3.12-slim

WORKDIR /app

# Dependencias Python (shapely/pyproj/pyogrio/geopandas traen wheels self-contained;
# no se necesitan libs de sistema GEOS/GDAL)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código
COPY . .

# Descargar el GeoJSON de GADM nivel 2 en build (el filesystem de runtime es efímero
# en Render y data/*.geojson está gitignored). ~1.1 MB.
RUN mkdir -p data && \
    python -c "import urllib.request; urllib.request.urlretrieve('https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_BOL_2.json','data/bolivia.geojson')" && \
    python -c "import json; d=json.load(open('data/bolivia.geojson')); assert len(d['features'])>0; print('GeoJSON OK:', len(d['features']), 'features')"

ENV ENVIRONMENT=production
EXPOSE 8001

# Render inyecta $PORT. El -b en CLI sobreescribe el bind 127.0.0.1 de gunicorn.conf.py.
# 1 worker (RAM acotada) + --preload para compartir el GeoDataFrame.
CMD ["sh", "-c", "gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT:-8001} --workers 1 --preload --timeout 30 --access-logfile - --error-logfile -"]
