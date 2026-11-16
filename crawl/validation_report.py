"""Final validation report -> results/validation.md
Human-human and LLM-human agreement on the 397-decision validation sample (codebook v0.3), overall and per stratum,
with 95% bootstrap confidence intervals (resampling repositories, to respect clustering)."""
import collections, json, os, random, statistics
from agreement import read_xlsx, DIMS, kappa, norm

ANN = '../annotation'
key = {k['vid']: k for k in json.load(open(f'{ANN}/validation_key.json'))}
A = read_xlsx(f'{ANN}/validation_annotator_A.xlsx'); B = read_xlsx(f'{ANN}/validation_annotator_B.xlsx')
llm_raw = {d['id']: d for d in map(json.loads, open('data/llm_all_qwen3.8-27b-xhigh-free.jsonl'))}
L = {v: {d: norm(llm_raw[k['id']][d]) for d in DIMS} for v, k in key.items() if 'error' not in llm_raw.get(k['id'], {'error': 1})}
ids = sorted(key)
cons = [i for i in ids if all(A[i][d] == B[i][d] for d in DIMS)]
C = {i: A[i] for i in cons}

def ci(X, Y, S, d, reps=2000, seed=1):
    """Cluster bootstrap over repositories."""
    by = collections.defaultdict(list)
    for i in S: by[key[i]['repo']].append(i)
    repos = list(by); rnd = random.Random(seed); ks = []
    for _ in range(reps):
        samp = [i for r in rnd.choices(repos, k=len(repos)) for i in by[r]]
        a, b = [X[i][d] for i in samp], [Y[i][d] for i in samp]
        if len(set(a) | set(b)) > 1: ks.append(kappa(a, b)[0])
    ks.sort(); return ks[int(.025 * len(ks))], ks[int(.975 * len(ks)) - 1]
def cell(X, Y, S, d):
    k, po = kappa([X[i][d] for i in S], [Y[i][d] for i in S]); lo, hi = ci(X, Y, S, d)
    return f'{k:.2f} [{lo:.2f}, {hi:.2f}] ({po:.0%})'
def row(c): return '| ' + ' | '.join(c) + ' |'

out = ['# Final validation (codebook v0.3)', '',
       f'Sample: {len(ids)} decisions, stratified by framework × provenance (66 per stratum plus the one decision the LLM failed to code), '
       'English only, pilot decisions excluded, at most two decisions per repository per stratum. Blind coding by two annotators (A, B) working independently.', '',
       'LLM: Qwen3.8-27B, open weights, temperature 0, frozen prompt (codebook v0.3), effort xhigh with one retry at medium.', '',
       "Cells: Cohen's kappa [95% CI, cluster bootstrap over repositories] (percentage agreement).", '']
for n, f in (('A', 'A'), ('B', 'B')):
    ss = __import__('openpyxl').load_workbook(f'{ANN}/validation_annotator_{f}.xlsx')['Sessions']
    tot = sum((r[3].hour * 60 + r[3].minute) - (r[2].hour * 60 + r[2].minute) for r in ss.iter_rows(min_row=2, values_only=True) if r[2] and r[3])
    out.append(f'Annotator {n}: {tot/60:.1f} h over {sum(1 for r in ss.iter_rows(min_row=2, values_only=True) if r[2])} sessions.')
out += ['', '## Overall', '', row(['Dimension', f'A–B (n={len(ids)})', f'A–LLM (n={len(L)})', f'B–LLM (n={len(L)})', f'Consensus–LLM (n={len([i for i in cons if i in L])})']), row(['---'] * 5)]
li = [i for i in ids if i in L]; lc = [i for i in cons if i in L]
for d in DIMS:
    out.append(row([d, cell(A, B, ids, d), cell(A, L, li, d), cell(B, L, li, d), cell(C, L, lc, d)]))
out += ['', '## Per stratum (kappa)', '', row(['Stratum', 'n', 'A–B mood', 'A–B locus', 'A–B concern', 'Cons–LLM mood', 'Cons–LLM locus', 'Cons–LLM concern']), row(['---'] * 8)]
for t, p in [('speckit', 'ASKED'), ('speckit', 'ASSUMED'), ('gsd', 'ASKED'), ('gsd', 'DELEGATED'), ('gsd', 'ASSUMED'), ('bmad', 'ASSUMED')]:
    S = [i for i in ids if key[i]['tool'] == t and key[i]['provenance'] == p]; Sc = [i for i in S if i in lc]
    def k(X, Y, Z, d):
        a, b = [X[i][d] for i in Z], [Y[i][d] for i in Z]
        return f'{kappa(a, b)[0]:.2f}' if len(set(a) | set(b)) > 1 else 'n/a (one category)'
    out.append(row([f'{t}/{p}', str(len(S))] + [k(A, B, S, d) for d in DIMS[:3]] + [k(C, L, Sc, d) for d in DIMS[:3]]))
out += ['', '## Disagreement patterns (A vs B)', '']
for d in DIMS[:3]:
    c = collections.Counter(tuple(sorted((A[i][d], B[i][d]))) for i in ids if A[i][d] != B[i][d])
    out.append(f'- **{d}**: ' + ', '.join(f'{a} vs {b} ({n})' for (a, b), n in c.most_common(6)))
out += ['', '## LLM errors against consensus', '']
for d in DIMS[:3]:
    c = collections.Counter((C[i][d], L[i][d]) for i in lc if C[i][d] != L[i][d])
    out.append(f'- **{d}** (human → LLM): ' + ', '.join(f'{a} → {b} ({n})' for (a, b), n in c.most_common(6)))
os.makedirs('../results', exist_ok=True)
open('../results/validation.md', 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
