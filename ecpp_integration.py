#!/usr/bin/env python3
import argparse
import json
import math
import subprocess
import time
from pathlib import Path

def proth_witness_check(N: int, a: int) -> bool:
    """Check Proth's theorem witness."""
    return pow(a, (N - 1) // 2, N) == N - 1

def run_ecpp(N: int, ecpp_cmd: str):
    """Run an external ECPP tool and return runtime, stdout, stderr, and cert path if found."""
    cmd = ecpp_cmd.format(N=N)
    t0 = time.time()
    try:
        proc = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=False
        )
    except Exception as e:
        return {
            "result": "error",
            "ms": None,
            "cmd": cmd,
            "stdout": "",
            "stderr": str(e),
            "cert_path": None
        }
    ms = round((time.time() - t0) * 1000, 2)
    cert_path = None
    for token in proc.stdout.split() + proc.stderr.split():
        if token.endswith(".ecpp") or token.endswith(".cert"):
            if Path(token).exists():
                cert_path = str(Path(token).resolve())
    return {
        "result": "ok" if proc.returncode == 0 else "fail",
        "ms": ms,
        "cmd": cmd,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "cert_path": cert_path
    }

def main():
    parser = argparse.ArgumentParser(description="Proth + ECPP integration tool")
    parser.add_argument("--n", type=int, help="n in k*2^n + 1")
    parser.add_argument("--k", type=int, help="k in k*2^n + 1")
    parser.add_argument("--N", type=int, help="Override N directly")
    parser.add_argument("--witness-a", type=int, help="Proth witness a")
    parser.add_argument("--digits", type=int, help="Reported digits")
    parser.add_argument("--ecpp-cmd", type=str, help="ECPP command string, use {N} placeholder")
    parser.add_argument("--arp-K", type=float, help="ARP param K")
    parser.add_argument("--arp-r", type=float, help="ARP param r")
    parser.add_argument("--arp-beta", type=float, help="ARP param beta")
    parser.add_argument("--out", type=str, required=True, help="Output JSON file")

    args = parser.parse_args()

    if args.N is not None:
        N = args.N
    elif args.n is not None and args.k is not None:
        N = args.k * pow(2, args.n) + 1
    else:
        raise ValueError("Must provide either --N or both --n and --k")

    record = {
        "N": str(N),
        "digits": args.digits if args.digits else len(str(N)),
        "params": {
            "n": args.n,
            "k": args.k
        },
        "proth_witness": None,
        "ecpp": None,
        "arp": None
    }

    # Proth witness check
    if args.witness_a:
        ok = proth_witness_check(N, args.witness_a)
        record["proth_witness"] = {
            "a": str(args.witness_a),
            "ok": ok
        }

    # ARP params
    if args.arp_K is not None or args.arp_r is not None or args.arp_beta is not None:
        record["arp"] = {
            "K": args.arp_K,
            "r": args.arp_r,
            "beta": args.arp_beta
        }

    # ECPP run
    if args.ecpp_cmd:
        ecpp_info = run_ecpp(N, args.ecpp_cmd)
        record["ecpp"] = ecpp_info

    Path(args.out).write_text(json.dumps(record, indent=2))
    print(f"Record written to {args.out}")

if __name__ == "__main__":
    main()
