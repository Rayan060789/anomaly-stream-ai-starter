
import os, json, time, uuid
from pathlib import Path
from datetime import datetime, timezone
import pandas as pd
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq
from joblib import load

EVENTS_LOG = Path("data/events.log")
LAKE_EVENTS = Path("lake/events")
LAKE_ANOMS = Path("lake/anomalies")
ARTIFACTS_DIR = Path("artifacts")
MODEL_PATH = ARTIFACTS_DIR / "model.joblib"

LAKE_EVENTS.mkdir(parents=True, exist_ok=True)
LAKE_ANOMS.mkdir(parents=True, exist_ok=True)

BATCH_SIZE = 500           # how many lines to process per flush
FLUSH_SECONDS = 3          # flush interval
WINDOW_SECONDS = 60        # simple window label for partitioning

FEATURES = ["metric1", "metric2", "metric3", "feature_a", "feature_b"]

def write_parquet(df: pd.DataFrame, outdir: Path):
    if df.empty:
        return
    ts = datetime.utcnow().replace(tzinfo=timezone.utc).strftime("%Y-%m-%dT%H-%M")
    dst = outdir / f"dt={ts}"
    dst.mkdir(parents=True, exist_ok=True)
    path = dst / f"part-{uuid.uuid4().hex}.parquet"
    table = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(table, path)
    print(f"[flush] wrote {len(df)} rows -> {path}")

def zscore_anomaly_score(X: np.ndarray):
    # simple fallback: max abs z-score across features
    mu = np.mean(X, axis=0)
    sd = np.std(X, axis=0) + 1e-6
    z = np.abs((X - mu) / sd)
    return z.max(axis=1)

def main():
    print("[processor] starting...")
    # try load model
    model = None
    if MODEL_PATH.exists():
        try:
            model = load(MODEL_PATH)
            print("[processor] loaded model:", MODEL_PATH)
        except Exception as e:
            print("[processor] failed to load model, using z-score fallback:", e)

    EVENTS_LOG.parent.mkdir(parents=True, exist_ok=True)
    # wait until log exists
    while not EVENTS_LOG.exists():
        print("[processor] waiting for events.log ..."); time.sleep(1)

    f = open(EVENTS_LOG, "r", encoding="utf-8")
    f.seek(0, os.SEEK_END)

    buf = []
    last_flush = time.time()

    while True:
        line = f.readline()
        if not line:
            if time.time() - last_flush >= FLUSH_SECONDS and buf:
                df = pd.DataFrame(buf)
                buf = []
                # write full events
                write_parquet(df, LAKE_EVENTS)

                # anomaly scoring
                X = df[FEATURES].to_numpy(dtype=float)
                if model is not None:
                    try:
                        score = (-model.score_samples(X))  # higher = more anomalous
                    except Exception as e:
                        print("[processor] model scoring failed, fallback:", e)
                        score = zscore_anomaly_score(X)
                else:
                    score = zscore_anomaly_score(X)
                df_anom = df.copy()
                df_anom["score"] = score
                df_anom["is_anomaly"] = (df_anom["score"] > np.percentile(score, 98)).astype(int)
                write_parquet(df_anom[df_anom["is_anomaly"] == 1], LAKE_ANOMS)

                last_flush = time.time()
            time.sleep(0.1)
            continue

        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
            buf.append(ev)
            if len(buf) >= BATCH_SIZE:
                df = pd.DataFrame(buf); buf = []
                write_parquet(df, LAKE_EVENTS)
                X = df[FEATURES].to_numpy(dtype=float)
                if model is not None:
                    try:
                        score = (-model.score_samples(X))
                    except Exception as e:
                        print("[processor] model scoring failed, fallback:", e)
                        score = zscore_anomaly_score(X)
                else:
                    score = zscore_anomaly_score(X)
                df_anom = df.copy()
                df_anom["score"] = score
                df_anom["is_anomaly"] = (df_anom["score"] > np.percentile(score, 98)).astype(int)
                write_parquet(df_anom[df_anom["is_anomaly"] == 1], LAKE_ANOMS)
                last_flush = time.time()
        except Exception as e:
            print("[warn] bad line, skipping:", e)

if __name__ == "__main__":
    main()
