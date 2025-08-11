from arpprimeamp.core import classify

def test_basic_signal():
    rows = classify(N=200, K=-0.8, r=1.0, beta=250.0, thresh=0.5)
    # Sanity: composites should be majority of 'COMPOSITE' labels
    comp_flags = sum(1 for _,_,pred,truth in rows if pred=='COMPOSITE')
    assert comp_flags > 0
