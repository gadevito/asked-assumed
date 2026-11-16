"""Inter-rater agreement on the pilot: Cohen's kappa per dimension, A vs B (and vs LLM if available)."""
import json, sys, collections, openpyxl

DIMS = ['mood', 'locus', 'concern', 'subcode']
def norm(v):
    v = (v or '').strip()
    return {'—': 'NONE', '': 'NONE'}.get(v, v.replace('ISO25010: ', 'ISO25010:').replace('Constraint: ', 'Constraint:'))
def read_xlsx(path):
    ws = openpyxl.load_workbook(path)['Annotate']
    return {r[0]: dict(zip(DIMS, map(norm, r[3:7])), note=r[7] or '') for r in ws.iter_rows(min_row=2, values_only=True) if r[0]}
def read_llm(path):
    out = {}
    for l in open(path):
        d = json.loads(l)
        if 'error' not in d: out[d['pid']] = {k: norm(d[k]) for k in DIMS}
    return out
def kappa(a, b):
    n = len(a); po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = collections.Counter(a), collections.Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(a) | set(b)) / n ** 2
    return (po - pe) / (1 - pe) if pe < 1 else 1.0, po
def compare(X, Y, label, subset=None):
    ids = [i for i in sorted(X) if i in Y and (subset is None or i in subset)]
    print(f'\n{label}  (n={len(ids)})')
    for dim in DIMS:
        k, po = kappa([X[i][dim] for i in ids], [Y[i][dim] for i in ids])
        print(f'  {dim:8s} kappa={k:5.2f}  agreement={po:.0%}')
    return ids

if __name__ == '__main__':
    A = read_xlsx('annotation/pilot_annotator_A_annotated.xlsx'); B = read_xlsx('annotation/pilot_annotator_B_annotated.xlsx')
    compare(A, B, 'A vs B')
    both_opt = {i for i in A if A[i]['mood'] == B[i]['mood'] == 'OPTATIVE'}
    compare(A, B, 'A vs B, only items both coded OPTATIVE', both_opt)
    for p in sys.argv[1:]:
        L = read_llm(p); compare(A, L, f'A vs LLM [{p}]'); compare(B, L, f'B vs LLM [{p}]')
