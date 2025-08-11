# ARPPrimeAmp Hybrid Workflow

This file defines the **cutover policy** and **interfaces** so collaborators can plug in CUDA acceleration for the ARP inner loop and we can certify primes end-to-end.

## Cutover Policy

- **n < 10^6 (classical range)**  
  1) **ARP prefilter:** compute `G_score` (with tuned `K, r, β, thresh`) and keep only prime-candidates.  
  2) **Proth test** (for N = k·2^n + 1).  
  3) **PRP test** (e.g., Baillie-PSW).  
  4) **ECPP certification** for accepted hits.

- **n ≥ 10^6 (moonshot range)**  
  1) **Proth test** → 2) **PRP** → 3) **ECPP** (skip ARP prefilter since √N dominates).

### Required Logging
- When ARP is used, record `{K, r, β, thresh}`, count of candidates before/after ARP, and composite recall/precision (or ROC/PR).  
- Always record hardware (CPU/GPU), library versions, wall time, candidate counts, and proof logs for certified primes.

## Integration Points

- `arpprimeamp/core.py` — CPU reference (`S_resonance`, `G_score`).  
- `arpprimeamp/cuda_arp.cu` — **CUDA kernel** providing a drop-in parallel `S_resonance` for batches of n.  
- `arpprimeamp/metrics.py` — ROC/PR, ablations, sweeps (coming).  
- `proth_search.py` — Proth hunter (fast path); will gain `--cuda-arp` and `--hybrid` flags.  
- `certify.py` — PRP/ECPP wrapper for certification (stub now; pluggable backends).

## CUDA ARP Interface (proposed)

- **Goal:** compute `S(n) = max_{2≤k≤⌊√n⌋} exp(-β Δ_{n,k}^2)` for a batch of n’s, where  
  `Δ_{n,k} = wrap_pi( 2·π_a·(n mod k)/n )`, `π_a = pi_adaptive(r, K)` is **constant** per batch.

- **Threading model:** 1 block per `n`; threads iterate `k` with striding; block-wide max-reduction.  
- **Kernel signature (C++/CUDA):**
  ```cpp
  extern "C" void arp_batch_S_resonance(
      const unsigned long long* n_values, int N,
      double K, double r, double beta,
      float* out_S  // length N
  );
  ```
- **Notes:**  
  - Precompute `pi_a = pi * (1 - K r^2 / 6 + K^2 r^4 / 120 - K^3 r^6 / 5040)` on host and pass as a kernel param if desired.  
  - Use fast-math for `exp` and modulo where acceptable; avoid 128-bit divisions.  
  - Reduce with warp shuffles then shared memory to a single `max` per block.

## Certification (PRP/ECPP) Stub

- `certify.py` exposes:
  ```bash
  python certify.py --in examples/proth_hits_fast.csv --out examples/proth_certified.csv
  ```
  It will run PRP first; ECPP when available. We’ll accept external backends (e.g., `pfgw`, `primo`, `mpir/gmp + ecpp` wrappers).

## Benchmark Protocol

- Fixed params for comparability: `K=-0.8, r=1.0, β∈{150,250,400}`, `thresh∈{0.4,0.5,0.6}`.  
- Report: candidates/sec, composite recall/precision, ROC AUC (when ARP used).  
- Hardware disclosure: GPU model, driver, CUDA version, clocks, power limits.  
- Artifact retention: CSVs, ROC/PR PNGs, proof logs.
