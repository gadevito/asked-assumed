"""Pilot calibration report -> results/pilot_calibration.md
Human-human agreement per round, codebook-rule adjustment, and LLM model selection (round 1 = dev, round 2 = held-out test)."""
import collections, json, os, sys
from agreement import read_xlsx, read_llm, DIMS, kappa

ANN = '../annotation'; DATA = 'data'
ROUNDS = {1: ('pilot_annotator_A_annotated', 'pilot_annotator_B_annotated', 'pilot_key'),
          2: ('pilot_annotator_A_round2_annotated', 'pilot_annotator_B_round2_annotated', 'pilot_key_round2')}
# (round, file, label, prompt version) — runs in chronological order
RUNS = [(1, 'llm_pilot_gpt-oss-120b-medium', 'gpt-oss-120b, constrained JSON, effort medium', 'v0.3'),
        (1, 'llm_pilot_v3b_medium', 'gpt-oss-120b, free reasoning, effort medium', 'v0.3'),
        (1, 'llm_pilot_v3b_high', 'gpt-oss-120b, free reasoning, effort high', 'v0.3 + indicative cues'),
        (1, 'llm_pilot_qwen3.6-35b-a3b-high-free', 'Qwen3.6-35B-A3B, free reasoning, effort high', 'v0.3 + indicative cues'),
        (1, 'llm_pilot_qwen3.8-27b-xhigh-free', 'Qwen3.8-27B, free reasoning, effort xhigh', 'v0.3 + indicative cues'),
        (2, 'llm_pilot2_gpt-oss-120b-medium', 'gpt-oss-120b, constrained JSON, effort medium', 'v0.3'),
        (2, 'llm_pilot2_qwen3.8-27b-xhigh-free', 'Qwen3.8-27B, free reasoning, effort xhigh (selected)', 'v0.3 + indicative cues')]

def rules(x):
    """Mechanical part of codebook v0.3 (R1 and PROJECT-PROCESS -> locus NA), applied to v0.2 human labels."""
    x = dict(x)
    if x['concern'] == 'PROJECT-PROCESS': x['locus'] = 'NA'
    if x['mood'] == 'OPTATIVE' and x['locus'] == 'MACHINE' and x['concern'] not in ('CONSTRAINT', 'PROJECT-PROCESS'):
        x['concern'] = 'CONSTRAINT'; x['subcode'] = 'Constraint:design & implementation'
    return x
def k(X, Y, ids, d): return kappa([X[i][d] for i in ids], [Y[i][d] for i in ids])[0]
def row(cells): return '| ' + ' | '.join(cells) + ' |'

out = ['# Pilot calibration results', '',
       'Codebook dimensions: D2 mood (Zave & Jackson 1997), D3 locus (WRSPM, Gunter et al. 2000), '
       'D4 concern and sub-code (Glinz 2007; ISO/IEC 25010:2023). Cohen\'s kappa; percentage agreement in brackets.', '',
       'Humans coded both rounds with codebook v0.2. Round 1 (50 decisions) was completed quickly and is treated as calibration; '
       'round 2 used 50 new decisions (no decision or repository in common with round 1). '
       'Sampling: stratified by framework × provenance, English only, at most one decision per repository.', '']
H = {}
for r, (fa, fb, fk) in ROUNDS.items():
    A, B = read_xlsx(f'{ANN}/{fa}.xlsx'), read_xlsx(f'{ANN}/{fb}.xlsx'); H[r] = (A, B)
    key = {x['pid']: x for x in json.load(open(f'{ANN}/{fk}.json'))}
    ids = sorted(A)
    out += [f'## Round {r}: human–human agreement (n={len(ids)})', '', row(['Dimension', 'A–B as coded (v0.2)', 'A–B after mechanical v0.3 rules']), row(['---'] * 3)]
    A2, B2 = {i: rules(v) for i, v in A.items()}, {i: rules(v) for i, v in B.items()}
    for d in DIMS:
        k1, p1 = kappa([A[i][d] for i in ids], [B[i][d] for i in ids]); k2, p2 = kappa([A2[i][d] for i in ids], [B2[i][d] for i in ids])
        out.append(row([d, f'{k1:.2f} ({p1:.0%})', f'{k2:.2f} ({p2:.0%})']))
    dis = [i for i in ids if any(A[i][d] != B[i][d] for d in DIMS)]
    out += ['', f'Disagreements: {len(dis)} decisions.', '', row(['ID', 'Framework/provenance', 'Dimension: A vs B']), row(['---'] * 3)]
    for i in dis:
        out.append(row([i, f"{key[i]['tool']}/{key[i]['provenance']}", '; '.join(f'{d}: {A[i][d]} vs {B[i][d]}' for d in DIMS if A[i][d] != B[i][d])]))
    same = [i for i in ids if A[i]['concern'] == B[i]['concern'] and A[i]['concern'] in ('SPECIFIC-QUALITY', 'CONSTRAINT')]
    out += ['', f'Sub-code agreement when concern agrees: {sum(A[i]["subcode"] == B[i]["subcode"] for i in same)}/{len(same)}.', '']

out += ['## LLM model selection', '',
        'Round 1 was used to develop the prompt (dev set); round 2 was held out as test set and coded once with the frozen prompt. '
        'Human labels are compared after the mechanical v0.3 rules, because the LLM prompt implements v0.3.', '',
        row(['Round', 'Configuration', 'Prompt', 'n', 'mood', 'locus', 'concern', 'sub-code', 'failed']), row(['---'] * 9)]
for r, f, label, pv in RUNS:
    p = f'{DATA}/{f}.jsonl'
    if not os.path.exists(p): continue
    raw = [json.loads(l) for l in open(p)]; L = read_llm(p)
    A, B = H[r]; A2, B2 = {i: rules(v) for i, v in A.items()}, {i: rules(v) for i, v in B.items()}
    ids = sorted(i for i in A2 if i in L); cons = [i for i in ids if all(A2[i][d] == B2[i][d] for d in DIMS)]
    cells = [f'{k(A2, L, ids, d):.2f} / {k(B2, L, ids, d):.2f} / **{k(A2, L, cons, d):.2f}**' for d in DIMS]
    out.append(row([str(r), label, pv, f'{len(ids)} (consensus {len(cons)})'] + cells + [str(sum("error" in x for x in raw))]))
out += ['', 'Cells: kappa vs A / vs B / **vs consensus** (items where A and B agree on all dimensions). Threshold: 0.70.', '',
        'Failed items on the test set (timeouts in long reasoning) were P30 and P39; the full run retries such items once at effort medium.']
os.makedirs('../results', exist_ok=True)
open('../results/pilot_calibration.md', 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
