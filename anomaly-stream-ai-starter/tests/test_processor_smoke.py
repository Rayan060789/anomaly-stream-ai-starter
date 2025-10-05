
from pathlib import Path
import json, time, os, pandas as pd
import subprocess, sys

def test_processor_smoke(tmp_path):
    # create fake events.log with two rows
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    log = data_dir / "events.log"
    ev = {"ts": "2025-01-01T00:00:00Z", "user_id":"u1",
          "metric1":1.0,"metric2":1.0,"metric3":1.0,"feature_a":0.1,"feature_b":0.2}
    with open(log, "w") as f:
        f.write(json.dumps(ev)+"\n")
        f.write(json.dumps(ev)+"\n")

    # run processor briefly
    p = subprocess.Popen([sys.executable, "services/processor/streaming_processor.py"])
    time.sleep(3)
    p.terminate()
    # expect some parquet files
    assert any(Path("lake/events").rglob("*.parquet"))
