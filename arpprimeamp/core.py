import math
from math import pi
from dataclasses import dataclass

def pi_adaptive(r: float, K: float) -> float:
    """Curvature-adjusted pi via small-circle expansion (to r^6)."""
    return pi * (1 - (K*r*r)/6 + (K*K*r**4)/120 - (K**3 * r**6)/5040)

def _phase_defect(n: int, k: int, pi_a: float) -> float:
    """Phase defect wrapped to [0, pi]."""
    x = (2 * pi_a * (n % k)) / n
    x = abs((x + pi) % (2*pi) - pi)
    return x

def S_resonance(n: int, K: float=-1.0, r: float=1.0, beta: float=200.0) -> float:
    pi_a = pi_adaptive(r, K)
    best = 0.0
    lim = int(math.isqrt(n))
    for k in range(2, lim+1):
        d = _phase_defect(n, k, pi_a)
        s = math.exp(-beta * d * d)
        if s > best:
            best = s
    return best

def G_score(n: int, alpha: float=1.0, mu: float=0.5, t: float=5.0, **kwargs) -> float:
    S = S_resonance(n, **kwargs)
    return (alpha/mu) * S * (1 - math.exp(-mu * t))

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

def classify(N: int=500, K: float=-0.8, r: float=1.0, beta: float=250.0, thresh: float=0.5,
             alpha: float=1.0, mu: float=0.5, t: float=5.0):
    """Return list of (n, G_score, pred, truth)."""
    out = []
    for n in range(2, N+1):
        g = G_score(n, alpha=alpha, mu=mu, t=t, K=K, r=r, beta=beta)
        pred = "COMPOSITE" if g >= thresh else "PRIME?"
        truth = "COMPOSITE" if not is_prime_det(n) else "PRIME"
        out.append((n, g, pred, truth))
    return out
