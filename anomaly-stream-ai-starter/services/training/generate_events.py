
import argparse, random, time, requests
from datetime import datetime, timezone

def gen_event():
    # mostly normal metrics, occasional spikes
    base = random.random()
    spike = random.random() < 0.02
    factor = 5.0 if spike else 1.0
    return {
        "ts": datetime.now(timezone.utc).isoformat(),
        "user_id": f"user-{random.randint(1, 10000)}",
        "metric1": round(abs(random.gauss(3, 1))*factor, 3),
        "metric2": round(abs(random.gauss(5, 1.2))*factor, 3),
        "metric3": round(abs(random.gauss(2, 0.7))*factor, 3),
        "feature_a": round(abs(random.gauss(1, 0.3)), 3),
        "feature_b": round(abs(random.gauss(4, 1.1)), 3),
        "tag": "spike" if spike else "normal"
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default="http://localhost:8000/events")
    ap.add_argument("--rate", type=int, default=100, help="events/sec")
    ap.add_argument("--duration", type=int, default=60, help="seconds to run")
    args = ap.parse_args()

    total = args.rate * args.duration
    print(f"Sending ~{total} events to {args.url} over {args.duration}s ... Ctrl+C to stop")
    try:
        for _ in range(total):
            ev = gen_event()
            requests.post(args.url, json=ev, timeout=3)
            time.sleep(1.0/args.rate)
    except KeyboardInterrupt:
        pass
    print("Done.")

if __name__ == "__main__":
    main()
