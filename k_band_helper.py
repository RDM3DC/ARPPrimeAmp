#!/usr/bin/env python3
"""Compute n,k bands for target digit counts.

Given a desired decimal digit count D, list the exponents n and small odd
k values such that N = k * 2**n + 1 has exactly D digits. This helps queue
Proth prime searches without manual log math.

Examples
--------
$ python k_band_helper.py 100
n=332: k=[1]
n=331: k=[1]
n=330: k=[1, 3]
n=329: k=[1, 3, 5, 7, 9]
"""
import argparse
import math
from typing import List, Tuple

LOG2_10 = 0.30103  # log10(2)


def bands_for_digits(digits: int, k_max: int = 9) -> List[Tuple[int, List[int]]]:
    """Return list of (n, [k...]) pairs yielding exactly ``digits`` digits.

    Only odd k in [1, k_max] are considered. Results are sorted by decreasing n.
    """
    if k_max < 1:
        raise ValueError("k_max must be >= 1")
    ks = [k for k in range(1, k_max + 1, 2)]
    # n limits based on smallest/largest k
    n_min = math.ceil((digits - 1 - math.log10(k_max)) / LOG2_10)
    n_max = math.floor((digits - 1e-12 - math.log10(1)) / LOG2_10)
    out: List[Tuple[int, List[int]]] = []
    for n in range(n_max, n_min - 1, -1):
        valid = [k for k in ks if math.floor(math.log10(k) + LOG2_10 * n) + 1 == digits]
        if valid:
            out.append((n, valid))
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("digits", type=int, help="target decimal digit count")
    p.add_argument("--k-max", type=int, default=9, help="max odd k to consider (inclusive)")
    args = p.parse_args()
    for n, ks in bands_for_digits(args.digits, args.k_max):
        if len(ks) == 1:
            print(f"n={n}: k={ks[0]}")
        else:
            print(f"n={n}: k={ks}")


if __name__ == "__main__":
    main()
