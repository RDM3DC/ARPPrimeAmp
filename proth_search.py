#!/usr/bin/env python3
"""
Proth prime hunter (fast path).

Searches N = k*2^n + 1 with k odd, k < 2^n.
If ∃ a s.t. a^((N-1)/2) ≡ -1 (mod N), N is prime (Proth's theorem).

Usage:
  python proth_search.py --n-min 20 --n-max 28 --samples 2000 --seed 42 --out examples/proth_hits.csv
"""
import argparse, random, time, csv

def is_proth_form(N:int, k:int, n:int) -> bool:
    return (k % 2 == 1) and (k < (1 << n)) and (N == k * (1 << n) + 1)

def proth_test(N:int, k:int, n:int, trials:int=10, rng=None):
    """Return (True, a) if Proth prime with witness a; else (False, None)."""
    if not is_proth_form(N, k, n):
        return False, None
    e = (N - 1) >> 1
    rng = rng or random.Random()
    for _ in range(trials):
        # choose random base in [2, N-2]
        a = rng.randrange(2, N-1) if N > 4 else 2
        if pow(a, e, N) == N - 1:
            return True, a
    return False, None

def run(n_min:int, n_max:int, samples:int, trials:int, seed:int, out_path:str):
    rng = random.Random(seed)
    t0 = time.time()
    hits = 0
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n","k","digits","a_base","N"])
        for n in range(n_min, n_max+1):
            limit = 1 << n
            for _ in range(samples):
                k = rng.randrange(1, limit, 2)
                N = k * limit + 1
                ok, a = proth_test(N, k, n, trials=trials, rng=rng)
                if ok:
                    hits += 1
                    w.writerow([n, k, len(str(N)), a, N])
    dt = time.time() - t0
    print(f"[proth_search] n=[{n_min},{n_max}] samples={samples} hits={hits} time={dt:.3f}s → {out_path}")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--n-min", type=int, default=8)
    p.add_argument("--n-max", type=int, default=22)
    p.add_argument("--samples", type=int, default=400, help="samples per n")
    p.add_argument("--trials", type=int, default=10, help="witness attempts per N")
    p.add_argument("--seed", type=int, default=2025)
    p.add_argument("--out", type=str, default="examples/proth_hits.csv")
    args = p.parse_args()
    run(args.n_min, args.n_max, args.samples, args.trials, args.seed, args.out)

if __name__ == "__main__":
    main()
