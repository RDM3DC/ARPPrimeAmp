#!/usr/bin/env python3
import argparse, math, json, gzip, csv, time
from math import pi

# ---------- Math ----------
def pi_adaptive(r: float, K: float) -> float:
    # 6th-order small-circle expansion
    return pi * (1 - (K*r*r)/6 + (K*K*r**4)/120 - (K**3 * r**6)/5040)

def phase_defect(n: int, k: int, pi_val: float) -> float:
    # wrap to [-pi, pi]
    x = (2.0 * pi_val * (n % k)) / n
    x = abs((x + pi) % (2*pi) - pi)
    return x

def S_resonance(n: int, pi_val: float, beta: float) -> float:
    best = 0.0
    lim = int(math.isqrt(n))
    for k in range(2, lim+1):
        d = phase_defect(n, k, pi_val)
        s = math.exp(-beta * d * d)
        if s > best:
            best = s
    return best

def G_score_from_S(S: float, alpha=1.0, mu=0.5, t=5.0) -> float:
    return (alpha/mu) * S * (1.0 - math.exp(-mu * t))

def is_prime_det(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    r = int(math.isqrt(n))
    f = 3
    while f <= r:
        if n % f == 0:
            return False
        f += 2
    return True

# ---------- Ablation ----------
def metrics_from_preds(truth_comp, pred_comp):
    # truth_comp, pred_comp are lists of bool
    total = len(truth_comp)
    tp = sum(1 for t,p in zip(truth_comp, pred_comp) if t and p)
    tn = sum(1 for t,p in zip(truth_comp, pred_comp) if (not t) and (not p))
    fp = sum(1 for t,p in zip(truth_comp, pred_comp) if (not t) and p)
    fn = sum(1 for t,p in zip(truth_comp, pred_comp) if t and (not p))
    acc = (tp + tn) / total
    precision = tp / (tp + fp) if (tp + fp) > 0 else float('nan')
    recall = tp / (tp + fn) if (tp + fn) > 0 else float('nan')
    crr = (tp + fp) / total  # fraction removed as "composite"
    survivors = total - (tp + fp)
    return {
        "accuracy": acc,
        "precision_composite": precision,
        "recall_composite": recall,
        "CRR": crr,
        "survivors": survivors,
        "TP": tp, "FP": fp, "TN": tn, "FN": fn
    }

def run_ablation(N, K, r, beta, thresh, alpha=1.0, mu=0.5, t=5.0):
    pi_a = pi_adaptive(r, K)
    pi_const = pi

    truth_comp = []
    G_pi_a = []
    G_pi   = []
    pred_a = []
    pred_c = []

    t0 = time.time()
    for n in range(2, N+1):
        tc = (not is_prime_det(n))
        truth_comp.append(tc)

        Sa = S_resonance(n, pi_a, beta)
        Ga = G_score_from_S(Sa, alpha=alpha, mu=mu, t=t)
        G_pi_a.append(Ga); pred_a.append(Ga >= thresh)

        Sc = S_resonance(n, pi_const, beta)
        Gc = G_score_from_S(Sc, alpha=alpha, mu=mu, t=t)
        G_pi.append(Gc);  pred_c.append(Gc >= thresh)
    t1 = time.time()

    m_a = metrics_from_preds(truth_comp, pred_a)
    m_c = metrics_from_preds(truth_comp, pred_c)
    meta = {
        "N": int(N), "K": float(K), "r": float(r), "beta": float(beta),
        "thresh": float(thresh), "alpha": float(alpha), "mu": float(mu), "t": float(t),
        "runtime_sec": float(t1 - t0)
    }
    return truth_comp, G_pi_a, pred_a, G_pi, pred_c, m_a, m_c, meta

def save_min_csv_gz(path, rows):
    # rows: iterable of dicts with minimal columns
    with gzip.open(path, "wt", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--N", type=int, default=20000)
    ap.add_argument("--K", type=float, default=-0.8)
    ap.add_argument("--r", type=float, default=1.0)
    ap.add_argument("--beta", type=float, default=250.0)
    ap.add_argument("--thresh", type=float, default=0.5)
    args = ap.parse_args()

    truth, G_a, pred_a, G_c, pred_c, m_a, m_c, meta = run_ablation(
        N=args.N, K=args.K, r=args.r, beta=args.beta, thresh=args.thresh
    )

    # minimal CSV (small!) — n, G_pi_a, pred_pi_a, G_pi, pred_pi
    rows = []
    for i, n in enumerate(range(2, args.N+1)):
        rows.append({
            "n": n,
            "G_pi_a": f"{G_a[i]:.6f}",
            "pred_comp_pi_a": int(pred_a[i]),
            "G_pi": f"{G_c[i]:.6f}",
            "pred_comp_pi": int(pred_c[i]),
        })
    csv_path = f"ablation_min_N{args.N}.csv.gz"
    save_min_csv_gz(csv_path, rows)

    # metrics JSON
    metrics_path = f"ablation_metrics_N{args.N}.json"
    with open(metrics_path, "w") as f:
        json.dump({"meta": meta, "pi_a": m_a, "pi": m_c}, f, indent=2)

    print("Wrote:", csv_path, "and", metrics_path)
    print("\u03c0_a metrics:", m_a)
    print("\u03c0   metrics:", m_c)
    print("meta:", meta)

if __name__ == "__main__":
    main()
