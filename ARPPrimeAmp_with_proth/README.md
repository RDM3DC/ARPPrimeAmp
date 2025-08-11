# ARPPrimeAmp

**ARP‑Amplified Adaptive‑π Prime Sieve** — a physics‑inspired composite filter that combines a curvature‑adjusted π (\(\pi_a\)) with the Adaptive Resistance Principle (ARP) to produce a continuous score \(G_n\) that lights up when a divisor exists.

> Not a magic prime oracle — think **sieve + signal**. Use ARPPrimeAmp to prune composites fast, then confirm survivors with a deterministic test (e.g., Miller–Rabin).

## Core Idea

**Adaptive π (small‑circle expansion):**
\[
\pi_a(r,K) \approx \pi\Big(1 - \frac{K r^2}{6} + \frac{K^2 r^4}{120} - \frac{K^3 r^6}{5040}\Big).
\]

**Phase‑defect per candidate divisor \(k\):**
\[
\Delta_{n,k}(K,r) = \Big\|\,\frac{2\,\pi_a(r,K)\,(n\bmod k)}{n}\,\Big\|_{\pi},
\]
wrapped to \([0,\pi]\).

**Resonance score:**
\[
S(n;K,r,\beta) = \max_{2\le k\le \lfloor\sqrt{n}\rfloor} \exp(-\beta\,\Delta_{n,k}^2).
\]

**ARP amplifier (closed‑form):**
\[
\tfrac{dG_n}{dt} = \alpha S(n) - \mu G_n
\quad\Rightarrow\quad
G_n(t) = \tfrac{\alpha}{\mu}\,S(n)\,(1-e^{-\mu t}).
\]

High \(G_n\) ⇒ likely **composite**. Low \(G_n\) ⇒ **prime‑candidate**.

## Quickstart

```bash
pip install -r requirements.txt
python -m arpprimeamp.cli --N 500 --K -0.8 --r 1.0 --beta 250 --thresh 0.5 --out examples/demo_500.csv
```

You’ll get a CSV with columns: `n, G_score, pred, truth`.

## Example Result (n ≤ 500)

Settings: \(K=-0.8, r=1.0, \beta=250, \text{thresh}=0.5\)

- **Accuracy:** 85.97%
- **Composite precision:** 85.23%
- **Composite recall:** 100% (no composites missed)
- **False positives:** 70 primes flagged as composite
- **True negatives (kept primes):** 25

Reproduce by running the command above.

## API (Python)

```python
from arpprimeamp.core import G_score, classify

scores = classify(N=1000, K=-0.8, r=1.0, beta=250.0, thresh=0.5)
```

## Files

- `arpprimeamp/core.py` — core math & scoring
- `arpprimeamp/cli.py` — command‑line tool to run ranges and write CSV
- `paramsweep.py` — sweep over (K, r, beta, thresh) and emit metrics CSV
- `examples/` — sample outputs
- `tests/` — sanity checks

## Why this matters

- **Interpretable**: spikes align with real divisors via a geometric phase‑defect, not a black‑box guess.
- **Tunable physics knobs**: \(K, r, \beta\) shape the separation behavior.
- **Parallel‑friendly**: shard ranges of \(n\) and hyperparams across threads/GPUs.

## Roadmap

- GPU/vectorized kernels
- ROC/PR curve generator
- Hybrid pipelines with Miller–Rabin & trial division
- Benchmark harness up to \(n=10^7\)

## License

MIT — see `LICENSE`.

---

## Proth Prime Hunt (fast path)

We include `proth_search.py` — a simple, fast hunter for primes of the form **N = k·2^n + 1** (with k odd, k < 2^n).  
It uses **Proth's theorem**: if there exists a base `a` such that `a^((N-1)/2) ≡ -1 (mod N)`, then `N` is prime.

Quick run:
```bash
python proth_search.py --n-min 8 --n-max 22 --samples 400 --seed 2025 --out examples/proth_hits_fast.csv
```

This will write a CSV with columns: `n, k, digits, a_base, N`.

**Note:** The ARP `G_score` filter is √N-costly and is best for classical-range sieves and science sweeps (ROC/PR). For huge N, Proth-first is the right ordering; then confirm with PRP/ECPP.
