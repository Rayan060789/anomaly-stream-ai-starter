
SHELL := /bin/bash

.PHONY: venv train api stream dash load

venv:
	python3 -m venv .venv && source .venv/bin/activate && pip install -U pip && pip install -r requirements.txt

train:
	python services/training/train_isoforest.py --out artifacts

api:
	uvicorn services.ingest_api.app:app --host 0.0.0.0 --port 8000 --reload

stream:
	python services/processor/streaming_processor.py

dash:
	streamlit run services/dashboard/streamlit_app.py

load:
	python services/training/generate_events.py --rate 100 --duration 60
