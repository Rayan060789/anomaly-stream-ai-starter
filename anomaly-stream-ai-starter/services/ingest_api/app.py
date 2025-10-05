
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from services.common.schemas import Event, EventBatch
import json, os, time
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path("data")
LOG_FILE = DATA_DIR / "events.log"
DATA_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="AI Anomaly Stream - Ingest API")

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

def _append_line(line: str):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

@app.post("/events")
async def post_event(event: Event):
    if not event.ts.tzinfo:
        event.ts = event.ts.replace(tzinfo=timezone.utc)
    payload = event.model_dump()
    payload["ts"] = event.ts.isoformat()
    _append_line(json.dumps(payload))
    return JSONResponse({"status": "accepted", "count": 1})

@app.post("/events/batch")
async def post_events(batch: EventBatch):
    count = 0
    for event in batch.events:
        if not event.ts.tzinfo:
            event.ts = event.ts.replace(tzinfo=timezone.utc)
        payload = event.model_dump()
        payload["ts"] = event.ts.isoformat()
        _append_line(json.dumps(payload))
        count += 1
    return JSONResponse({"status": "accepted", "count": count})
