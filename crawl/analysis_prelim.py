"""Preliminary RQ1/RQ2 tables from LLM codes (to be confirmed after final human validation)."""
import json, collections
D = {d['id']: d for d in map(json.loads, open('data/decisions.jsonl'))}
L = [json.loads(l) for l in open('data/llm_all_qwen3.8-27b-xhigh-free.jsonl')]
rows = [dict(D[c['id']], **{k: c[k] for k in ('mood', 'locus', 'concern', 'subcode')}) for c in L if 'error' not in c]
viol = sum(1 for r in rows if r['mood'] == 'OPTATIVE' and r['locus'] == 'MACHINE' and r['concern'] not in ('CONSTRAINT', 'PROJECT-PROCESS'))
print(f'coded {len(rows)}; R1 violations by the model: {viol}')
def pct(n, d): return f'{100*n/d:5.1f}%' if d else '   - '
print('\nTool/provenance        n   indicative | of optative: solution-space  high-stakes  project/process')
for t in ['speckit', 'gsd', 'bmad']:
    for p in ['ASKED', 'DELEGATED', 'ASSUMED']:
        g = [r for r in rows if r['tool'] == t and r['provenance'] == p]
        if not g: continue
        opt = [r for r in g if r['mood'] == 'OPTATIVE']
        sol = sum(1 for r in opt if r['locus'] == 'MACHINE' or r['subcode'] == 'Constraint:design & implementation')
        hs = sum(1 for r in opt if r['subcode'] in ('ISO25010:security', 'ISO25010:safety', 'Constraint:legal'))
        pp = sum(1 for r in opt if r['concern'] == 'PROJECT-PROCESS')
        print(f'{t:8s} {p:10s} {len(g):5d}   {pct(len(g)-len(opt), len(g))}   |   {pct(sol, len(opt))}        {pct(hs, len(opt))}      {pct(pp, len(opt))}')
print('\nConcern of OPTATIVE decisions, ASKED vs ASSUMED (all tools):')
for p in ['ASKED', 'ASSUMED']:
    opt = [r for r in rows if r['provenance'] == p and r['mood'] == 'OPTATIVE']
    c = collections.Counter(r['concern'] for r in opt)
    print(f'  {p:8s} n={len(opt):4d} ' + '  '.join(f'{k}:{pct(v, len(opt)).strip()}' for k, v in c.most_common()))
