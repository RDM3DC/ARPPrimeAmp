import argparse, csv
from arpprimeamp.core import classify

def main():
    p = argparse.ArgumentParser(description="ARPPrimeAmp CLI: run sieve+signal and export CSV.")
    p.add_argument('--N', type=int, default=500)
    p.add_argument('--K', type=float, default=-0.8)
    p.add_argument('--r', type=float, default=1.0)
    p.add_argument('--beta', type=float, default=250.0)
    p.add_argument('--thresh', type=float, default=0.5)
    p.add_argument('--alpha', type=float, default=1.0)
    p.add_argument('--mu', type=float, default=0.5)
    p.add_argument('--t', type=float, default=5.0)
    p.add_argument('--out', type=str, default='examples/demo.csv')
    args = p.parse_args()

    rows = classify(N=args.N, K=args.K, r=args.r, beta=args.beta, thresh=args.thresh,
                    alpha=args.alpha, mu=args.mu, t=args.t)
    with open(args.out, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['n','G_score','pred','truth'])
        for n,g,pred,truth in rows:
            w.writerow([n, f"{g:.9f}", pred, truth])
    print(f"Wrote {args.out} with {len(rows)} rows.")

if __name__ == '__main__':
    main()
