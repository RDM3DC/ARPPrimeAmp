import itertools, csv
from statistics import mean
from arpprimeamp.core import classify

def evaluate(N, K, r, beta, thresh):
    rows = classify(N=N, K=K, r=r, beta=beta, thresh=thresh)
    tp = sum(1 for _,_,pred,truth in rows if pred=='COMPOSITE' and truth=='COMPOSITE')
    tn = sum(1 for _,_,pred,truth in rows if pred=='PRIME?' and truth=='PRIME')
    fp = sum(1 for _,_,pred,truth in rows if pred=='COMPOSITE' and truth=='PRIME')
    fn = sum(1 for _,_,pred,truth in rows if pred=='PRIME?' and truth=='COMPOSITE')
    acc = (tp+tn)/len(rows)
    prec = tp/(tp+fp) if (tp+fp)>0 else float('nan')
    rec = tp/(tp+fn) if (tp+fn)>0 else float('nan')
    return acc, prec, rec, tp, fp, tn, fn

def main():
    N = 1000
    Ks = [-1.2, -0.8, -0.5]
    rs = [0.7, 1.0, 1.3]
    betas = [150.0, 250.0, 400.0]
    thresholds = [0.4, 0.5, 0.6]

    with open('examples/sweep_results.csv','w',newline='') as f:
        w = csv.writer(f)
        w.writerow(['N','K','r','beta','thresh','accuracy','precision_comp','recall_comp','TP','FP','TN','FN'])
        for K,r,beta,thresh in itertools.product(Ks, rs, betas, thresholds):
            acc,prec,rec,tp,fp,tn,fn = evaluate(N, K, r, beta, thresh)
            w.writerow([N,K,r,beta,thresh,acc,prec,rec,tp,fp,tn,fn])
    print("Wrote examples/sweep_results.csv")

if __name__ == '__main__':
    main()
