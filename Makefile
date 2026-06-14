.PHONY: install data dev prod test

install:
	python -m venv venv
	venv/Scripts/pip install -r requirements.txt

data:
	bash scripts/download_data.sh

dev:
	uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload

prod:
	gunicorn app.main:app -c gunicorn.conf.py

test:
	pytest tests/ -v
