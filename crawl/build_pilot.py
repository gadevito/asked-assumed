"""Blinded pilot annotation workbooks (2 annotators) + key. Stratified tool x provenance, English only, max 1 decision per repo."""
import json, random, re, collections, sys, os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
D = [json.loads(l) for l in open('data/decisions.jsonl')]
ROUND = int(sys.argv[1]) if len(sys.argv) > 1 else 1
SUFFIX = '' if ROUND == 1 else f'_round{ROUND}'
prev = []  # exclude decisions and repositories used in earlier rounds
for r in range(1, ROUND):
    p = '../annotation/pilot_key.json' if r == 1 else f'../annotation/pilot_key_round{r}.json'
    prev += json.load(open(p))
prev_repos = {k['repo'] for k in prev}
STRATA = [('speckit','ASKED',8),('speckit','ASSUMED',9),('gsd','ASKED',8),('gsd','DELEGATED',8),('gsd','ASSUMED',8),('bmad','ASSUMED',9)]
rnd = random.Random(20261019 + ROUND - 1); S = []; used = set(prev_repos)
for t, p, n in STRATA:
    pool = [d for d in D if d['tool']==t and d['provenance']==p and d['lang_en'] and 15 < len(d['text']) < 700]
    rnd.shuffle(pool); k = 0
    for d in pool:
        if d['repo'] in used: continue
        used.add(d['repo']); S.append(d); k += 1
        if k == n: break
rnd.shuffle(S)
for i, d in enumerate(S, 1):
    d['pid'] = f'P{i:02d}'
    d['shown'] = re.sub(r'\*\*', '', f"Q: {d['text']}\nA: {d['answer']}" if d.get('answer') else d['text'])
json.dump([{k: d[k] for k in ['pid','id','tool','provenance','section','repo','file','shown']} for d in S], open(f'../annotation/pilot_key{SUFFIX}.json','w'), indent=1, ensure_ascii=False)
print('selected', len(S), collections.Counter((d['tool'], d['provenance']) for d in S))

F = 'Arial'; thin = Side(style='thin', color='BFBFBF')
SUB = ['—'] + [f'ISO25010: {x}' for x in ['functional suitability','performance efficiency','compatibility','interaction capability','reliability','security','maintainability','flexibility','safety']] \
      + [f'Constraint: {x}' for x in ['physical','legal','cultural','environmental','design & implementation','interface']]
GUIDE = [('Pilot annotation — "Asked or Assumed?"  (codebook v0.2)', 'h1'), ('Start time (hh:mm) →', ''), ('End time (hh:mm) →', ''),
 ('Edit ONLY the yellow cells in sheet "Annotate" (columns D–H). Work independently; do not discuss until both are done.', ''),
 ('Tool and provenance are hidden on purpose (blind coding). Open the link only if the text alone is not enough.', ''), ('', ''),
 ('D2 Mood (Zave & Jackson 1997)', 'h'),
 ('INDICATIVE — how the world is, independent of the system (domain knowledge). Test: would it remain true if the system were never built? → INDICATIVE', ''),
 ('OPTATIVE — what the system should be or do, or a choice about the system.', ''), ('', ''),
 ('D3 Locus (Gunter et al. 2000, WRSPM) — only if OPTATIVE, else NA', 'h'),
 ('ENV — refers only to environment phenomena: goals, business rules, outcomes in the world.', ''),
 ('INTERFACE — phenomena shared at the machine boundary: inputs/outputs, UI behaviour, externally exposed API contracts.', ''),
 ('MACHINE — phenomena hidden inside the machine: architecture, libraries, data structures, algorithms, file layout.', ''),
 ('Test: can an observer outside the machine check the decision without seeing the code? No → MACHINE.', ''), ('', ''),
 ('D4 Concern (Glinz 2007) — only if OPTATIVE, else NA. Ask in order, take the first YES:', 'h'),
 ('1 FUNCTIONAL — stated to specify behaviour, data, input, or reaction to stimuli?', ''),
 ('2 PERFORMANCE — stated because of timing, speed, data volume, throughput?', ''),
 ('3 SPECIFIC-QUALITY — a specific quality the system/component shall have? → also pick an ISO 25010 sub-code', ''),
 ('4 CONSTRAINT — any other restriction on what/how, or a prescribed solution element? → also pick a constraint sub-code', ''),
 ('5 PROJECT-PROCESS — about the project/development process, not the system (testing strategy, CI, phasing, conventions)', ''), ('', ''),
 ('Worked examples (not to be coded):', 'h'),
 ('"Q: How long should sessions last? A: 30 minutes, then automatic logout"  →  OPTATIVE | INTERFACE | FUNCTIONAL | —', ''),
 ('"Users access the app from company laptops on the corporate VPN"  →  INDICATIVE | NA | NA | —', ''),
 ('"Use SQLite with WAL mode for local storage"  →  OPTATIVE | MACHINE | CONSTRAINT | Constraint: design & implementation', '')]
def build(name):
    wb = Workbook(); g = wb.active; g.title = 'Guide'; g.column_dimensions['A'].width = 140
    for i, (txt, st) in enumerate(GUIDE, 1):
        c = g.cell(i, 1, txt); c.alignment = Alignment(wrap_text=True)
        c.font = Font(name=F, bold=bool(st), size=13 if st == 'h1' else 11 if st == 'h' else 10)
    g.column_dimensions['B'].width = 14
    for r in (2, 3): g.cell(r, 2).fill = PatternFill('solid', fgColor='FFF2CC'); g.cell(r, 2).border = Border(top=thin, bottom=thin, left=thin, right=thin)
    ws = wb.create_sheet('Annotate')
    ws.append(['ID','Decision text (as recorded)','Source link','D2 Mood','D3 Locus','D4 Concern','D4 Sub-code','Notes / doubts'])
    for c in ws[1]:
        c.font = Font(name=F, bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='1F3864'); c.alignment = Alignment(wrap_text=True, vertical='center')
    for d in S:
        ws.append([d['pid'], d['shown'], 'open', None, None, None, None, None]); r = ws.max_row
        ws.cell(r, 3).hyperlink = f"https://github.com/{d['repo']}/blob/HEAD/{d['file']}"
    for w, col in zip([6,90,8,13,13,18,32,30], 'ABCDEFGH'): ws.column_dimensions[col].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font = Font(name=F, color='0563C1', underline='single') if c.column == 3 else Font(name=F, size=10)
            c.alignment = Alignment(wrap_text=True, vertical='top'); c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
            if 4 <= c.column <= 8: c.fill = PatternFill('solid', fgColor='FFF2CC')
    ws.freeze_panes = 'B2'
    L = wb.create_sheet('Lists'); L.sheet_state = 'hidden'
    for i, v in enumerate(SUB, 1): L.cell(i, 1, v)
    n = len(S) + 1
    for col, opts in [('D','"INDICATIVE,OPTATIVE"'),('E','"ENV,INTERFACE,MACHINE,NA"'),('F','"FUNCTIONAL,PERFORMANCE,SPECIFIC-QUALITY,CONSTRAINT,PROJECT-PROCESS,NA"'),('G', f'Lists!$A$1:$A${len(SUB)}')]:
        dv = DataValidation(type='list', formula1=opts, allow_blank=True); ws.add_data_validation(dv); dv.add(f'{col}2:{col}{n}')
    wb.active = 1; wb.save(f'../annotation/{name}')
build(f'pilot_annotator_A{SUFFIX}.xlsx'); build(f'pilot_annotator_B{SUFFIX}.xlsx')
