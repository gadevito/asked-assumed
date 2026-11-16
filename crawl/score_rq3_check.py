"""Score the current RQ3 parser against annotators' readings of a check sheet.
Usage: python score_rq3_check.py v2 A B   |   python score_rq3_check.py v3 A"""
import json, sys, openpyxl
VER, ANN = sys.argv[1], sys.argv[2:]
LABEL = {'recommended option chosen': 'REC-ACCEPTED', 'another listed option chosen': 'ALT-OPTION', 'free answer / no option ticked': 'FREE',
         'no option marked as recommended': 'N/A', 'human handed the choice back ("you decide")': 'DEFER-BACK'}
key = json.load(open(f'../annotation/rq3_check_{VER}_key.json'))
R = {a: {r[0]: r for r in openpyxl.load_workbook(f'../annotation/rq3_{VER}_in/rq3_extractor_check_{VER}_{a}.xlsx', data_only=True)['Check']
         .iter_rows(min_row=2, values_only=True) if r[0]} for a in ANN}
B = {}
for l in open('data/rq3_blocks.jsonl'):
    b = json.loads(l); B.setdefault((b['repo'], b['file']), []).append(b)
def gold(a, q, old):
    r = R[a][q]
    if str(r[6] or '').strip().upper().startswith('EXCLUDE'): return 'EXCLUDED'   # multi-select or sub-decision table
    return old if r[4] == 'YES' else LABEL[r[5]]
ok = {f'{w} {a}': 0 for w in ('sheet', 'now') for a in ANN}; excl = []
for k in key:
    q, old = k['qid'], k['behaviour']; raw = R[ANN[0]][q][1]
    c = [b for b in B.get((k['repo'], k['file']), []) if b['raw'].strip() == raw.strip()]
    new = c[0]['behaviour'] if len(c) == 1 else ('EXCLUDED' if not c else f'?{len(c)}')
    if new == 'EXCLUDED': excl.append(q)
    g = {a: gold(a, q, old) for a in ANN}
    for a in ANN: ok[f'sheet {a}'] += old == g[a]; ok[f'now {a}'] += new == g[a]
    if any(new != g[a] or old != g[a] for a in ANN): print(f'{q}  sheet {old:12} now {new:12} | ' + '  '.join(f'{a} {g[a]}' for a in ANN))
print(VER, ok, '| excluded by parser now:', excl)
