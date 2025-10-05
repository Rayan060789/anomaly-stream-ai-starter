
# AI Anomaly Stream — Real‑Time Anomaly Detection Platform (SWE + Data + AI)

**AI-powered streaming platform** that ingests real-time events, applies **online anomaly detection** (Isolation Forest baseline + statistical fallback), stores both events and anomalies in a lakehouse format (Parquet), and presents a **live dashboard**. Built to demonstrate **Software Engineering** + **Data Engineering** + **Applied ML** in a single, production‑styled repo.

---

## ✨ Highlights
- **SWE**: FastAPI ingest service, modular code, tests, Makefile, clear runbook
- **DE**: streaming processor, Parquet lake, DuckDB analytics, Streamlit dashboard
- **AI/ML**: Isolation Forest model (joblib), online stats fallback, drift hooks
- **Portable**: Runs locally in “Lite Mode” (no Kafka). Optional Docker/Kafka in Phase 2

---

## 🧱 Architecture (Lite Mode)
```
[Load Generator] --HTTP--> [FastAPI Ingest] --append NDJSON--> data/events.log
                                                 |
                                                 v
                                       [Streaming Processor] --writes--> lake/events/*.parquet
                                                                        lake/anomalies/*.parquet
                                                                        |
                                                                        v
                                                                 [Streamlit Dashboard]
```
**Notes**
- Ingest accepts single or batched JSON events.
- Processor tails `data/events.log`, computes features, scores anomalies with a saved IsolationForest (`artifacts/model.joblib`) or a statistical fallback, writes Parquet.
- Dashboard uses DuckDB to query Parquet and visualize trends + recent anomalies.

---

## 🧭 Quickstart (Lite Mode, no Docker)
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1) Train a baseline model & create artifacts/
python services/training/train_isoforest.py --out artifacts

# 2) Start the ingest API (terminal A)
uvicorn services.ingest_api.app:app --host 0.0.0.0 --port 8000 --reload

# 3) Start the streaming processor (terminal B)
python services/processor/streaming_processor.py

# 4) Start the dashboard (terminal C)
streamlit run services/dashboard/streamlit_app.py

# 5) Generate events (terminal D)
python services/training/generate_events.py --rate 100 --duration 60
```
Open the dashboard URL printed by Streamlit and watch anomalies appear in near real time.

---

## 📁 Repository Layout
```
anomaly-stream-ai/
  services/
    ingest_api/app.py            # FastAPI: /healthz, /events
    processor/streaming_processor.py  # tails events.log, scores anomalies, writes Parquet
    dashboard/streamlit_app.py   # DuckDB queries, charts, tables
    training/train_isoforest.py  # trains IsolationForest & saves joblib
    training/generate_events.py  # synthetic event generator (HTTP posts)
    common/schemas.py            # Pydantic models & helpers
  docker/
    docker-compose.yaml          # (Phase 2) Redpanda/Kafka + services wiring
  tests/
    test_processor_smoke.py      # minimal test: writes a line, expects parquet
  assets/                        # diagrams/screenshots
  requirements.txt
  Makefile
  README.md
  .gitignore
```

---

## 🔬 Data Schema
Each event has:
- `ts` (RFC3339 string), `user_id` (str), `metric1..3` (floats), `feature_a/b` (ints/floats), and optional tags.

Anomalies are rows with an anomaly **score**, **label** (0/1), and window timestamp.

---

## 🧪 Model
Baseline = **Isolation Forest** trained on synthetic normal behavior.  
Fallback = rolling **z-score** (mean/std over window) when model missing.  
Extendable to Autoencoder/LSTM later.

---

## 📊 Dashboard Panels
- Anomaly count over time
- Top users with most anomalies
- Recent anomalies table with scores
- Global metrics (event rate, anomaly rate)

---

## 🧰 Make Targets
```bash
make venv         # create & install deps
make train        # train model → artifacts/model.joblib
make api          # run FastAPI
make stream       # run processor
make dash         # run Streamlit
make load         # run generator
```

---

## 🧪 Minimal Tests
- Processor smoke test: write a sample line to `events.log`, run a quick loop, expect at least one parquet file.

---

## 🧾 Benchmarks Template (fill after your first run)
| Metric | Target | Your Result | Notes |
|---|---:|---:|---|
| End‑to‑end p95 (ingest→anomaly sink) | < 2 s |  |  |
| Sustained throughput | 500 evts/s |  | CPU & I/O bound |
| False positive rate | < 2% |  | validate with labeled set |

---

## 🧪 Phase 2 (Docker/Kafka)
1) Enable **Redpanda** (Kafka‑compatible) via `docker-compose.yaml`.
2) Modify processor to consume from Kafka topic `events` (Faust/Confluent Python).
3) Add Prometheus + Grafana; publish FastAPI/processor metrics (latency histograms).

---

## 🧯 Runbook (Ops)
- **Backpressure**: processor lagging? Flush interval too high? Reduce batch size or parallelize feature computation.
- **Model drift**: distribution shift? Add a job to retrain daily on last N hours and compare KS‑stat/p‑values; if drift detected, auto‑promote new model after canary.
- **No data**: check `/healthz`, then generator; ensure `events.log` is growing.

---

## 🧠 AI Extensions
- LLM‑based anomaly explanations (summaries for the last 50 anomalous events).  
- Feature store integration; embedding‑based detectors.  
- Online learning with partial_fit models.

---

## 📝 License
MIT
