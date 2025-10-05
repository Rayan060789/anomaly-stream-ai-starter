
import argparse, os, joblib, numpy as np
from sklearn.ensemble import IsolationForest

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="artifacts")
    ap.add_argument("--n", type=int, default=50000)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    # synthetic normal-ish distribution
    rng = np.random.default_rng(123)
    X = np.column_stack([
        np.abs(rng.normal(3, 1, args.n)),
        np.abs(rng.normal(5, 1.2, args.n)),
        np.abs(rng.normal(2, 0.7, args.n)),
        np.abs(rng.normal(1, 0.3, args.n)),
        np.abs(rng.normal(4, 1.1, args.n)),
    ])

    clf = IsolationForest(n_estimators=200, contamination=0.02, random_state=42)
    clf.fit(X)
    path = os.path.join(args.out, "model.joblib")
    joblib.dump(clf, path)
    print("Saved model to", path)

if __name__ == "__main__":
    main()
