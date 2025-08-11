#!/usr/bin/env python3
"""
certify.py — PRP/ECPP certification stub.

Usage:
  python certify.py --in examples/proth_hits_fast.csv --out examples/proth_certified.csv
"""
import argparse, csv, sys, math

def prp_test(n: int, bases=(2,3,5,7,11,13,17)) -> bool:
    # Simple Baillie-PSW-like placeholder: run a few strong probable prime tests.
    # (For production, replace with a robust library.)
    def miller_rabin(n, a):
        if n % a == 0:
            return n == a
        d = n - 1
        s = 0
        while d % 2 == 0:
            d //= 2
            s += 1
        x = pow(a, d, n)
        if x == 1 or x == n-1:
            return True
        for _ in range(s-1):
            x = (x * x) % n
            if x == n-1:
                return True
        return False

    if n < 2: return False
    small_primes = [2,3,5,7,11,13,17,19,23,29]
    for p in small_primes:
        if n == p: return True
        if n % p == 0: return False
    for a in bases:
        if a >= n: break
        if not miller_rabin(n, a): return False
    return True

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--out", dest="outp", required=True)
    args = p.parse_args()

    with open(args.inp, newline="") as f, open(args.outp, "w", newline="") as g:
        r = csv.DictReader(f)
        w = csv.DictWriter(g, fieldnames=r.fieldnames + ["PRP_pass"])
        w.writeheader()
        for row in r:
            N = int(row["N"])
            row["PRP_pass"] = "YES" if prp_test(N) else "NO"
            w.writerow(row)

    print(f"[certify] wrote {args.outp}")

if __name__ == "__main__":
    main()
