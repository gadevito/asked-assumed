"""Final validation sample (codebook v0.3): blinded workbooks for two annotators + key.
Stratified by tool x provenance (equal allocation), English only, pilot decisions excluded,
at most 2 decisions per repository per stratum. The decision the LLM failed to code is always included."""
import json, random, re, collections
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation

SEED = 20261025
PER_STRATUM = 66
STRATA = [('speckit', 'ASKED'), ('speckit', 'ASSUMED'), ('gsd', 'ASKED'), ('gsd', 'DELEGATED'), ('gsd', 'ASSUMED'), ('bmad', 'ASSUMED')]
D = [json.loads(l) for l in open('data/decisions.jsonl')]
llm = {d['id']: d for d in map(json.loads, open('data/llm_all_qwen3.8-27b-xhigh-free.jsonl'))}
pilot = {k['id'] for f in ('pilot_key.json', 'pilot_key_round2.json') for k in json.load(open(f'../annotation/{f}'))}
failed = [i for i, c in llm.items() if 'error' in c]

rnd = random.Random(SEED); S = [d for d in D if d['id'] in failed]
for t, p in STRATA:
    pool = [d for d in D if d['tool'] == t and d['provenance'] == p and d['lang_en'] and d['id'] in llm
            and d['id'] not in pilot and d['id'] not in failed and 15 < len(d['text']) < 700]
    rnd.shuffle(pool); per_repo = collections.Counter(); k = 0
    for d in pool:
        if per_repo[d['repo']] >= 2: continue
        per_repo[d['repo']] += 1; S.append(d); k += 1
        if k == PER_STRATUM: break
rnd.shuffle(S)
for i, d in enumerate(S, 1):
    d['vid'] = f'V{i:03d}'
    d['shown'] = re.sub(r'\*\*', '', f"Q: {d['text']}\nA: {d['answer']}" if d.get('answer') else d['text'])
json.dump([{k: d[k] for k in ['vid', 'id', 'tool', 'provenance', 'section', 'repo', 'file', 'shown']} for d in S],
          open('../annotation/validation_key.json', 'w'), indent=1, ensure_ascii=False)
print('selected', len(S), collections.Counter((d['tool'], d['provenance']) for d in S))

F = 'Arial'; thin = Side(style='thin', color='BFBFBF'); YEL = PatternFill('solid', fgColor='FFF2CC')
SUB = ['—'] + [f'ISO25010: {x}' for x in ['functional suitability', 'performance efficiency', 'compatibility', 'interaction capability',
               'reliability', 'security', 'maintainability', 'flexibility', 'safety']] \
      + [f'Constraint: {x}' for x in ['physical', 'legal', 'cultural', 'environmental', 'design & implementation', 'interface']]
GUIDE = [
 ('Validation annotation — "Asked or Assumed?"  (codebook v0.3)', 'h1'),
 ('Edit ONLY the yellow cells. Work independently; do not discuss items until both annotators have finished.', ''),
 ('Tool and provenance are hidden on purpose (blind coding). Open the link only if the text alone is not enough.', ''),
 ('You can work in several sessions: log each session in the sheet "Sessions".', ''), ('', ''),
 ('D2 Mood (Zave & Jackson 1997)', 'h'),
 ('INDICATIVE — how the world is, independent of the system. Test: would it remain true if the system were never built? → INDICATIVE.', ''),
 ('INDICATIVE also covers machines already in the environment: behaviour or availability of external services, APIs, models, third-party libraries and tools; facts about existing code, data, infrastructure or capacity; expectations about users, markets or competitors — even when phrased with "will" or "should".', ''),
 ('OPTATIVE — what the system should be or do, or a choice about the system.', ''), ('', ''),
 ('D3 Locus (Gunter et al. 2000, WRSPM) — only if OPTATIVE; INDICATIVE and PROJECT-PROCESS → NA', 'h'),
 ('ENV — environment phenomena only: goals, business rules, outcomes in the world.', ''),
 ('INTERFACE — phenomena shared at the machine boundary: inputs/outputs, UI behaviour, API contracts, signals to other programs or devices, files users edit.', ''),
 ('MACHINE — phenomena hidden inside the machine: architecture, libraries, data structures, algorithms, internal configuration.', ''),
 ('Test: can an observer outside the machine check the decision without seeing the code? No → MACHINE.', ''), ('', ''),
 ('D4 Concern (Glinz 2007) — only if OPTATIVE, else NA. Ask in order, take the first YES:', 'h'),
 ('1 FUNCTIONAL — stated to specify behaviour, data, input, or reaction to stimuli?', ''),
 ('2 PERFORMANCE — stated because of timing, speed, data volume, throughput?', ''),
 ('3 SPECIFIC-QUALITY — a specific quality the system/component shall have? → pick the ISO/IEC 25010:2023 sub-code', ''),
 ('4 CONSTRAINT — any other restriction on what/how, or a prescribed solution element? → pick the constraint sub-code', ''),
 ('5 PROJECT-PROCESS — about the project/development process, not the system (testing strategy, CI, phasing, conventions)', ''), ('', ''),
 ('Boundary rules (v0.3)', 'h'),
 ('R1 OPTATIVE + MACHINE → CONSTRAINT (design & implementation) or PROJECT-PROCESS. FUNCTIONAL, PERFORMANCE, SPECIFIC-QUALITY need ENV or INTERFACE.', ''),
 ('R2 If the text states an explicit reason, the reason decides the concern (subject to R1).', ''),
 ('R3 INTERFACE includes other programs, processes, devices and files edited by users; MACHINE only if nothing outside can observe it.', ''),
 ('R4 A business rule about domain entities is ENV even if its effect is displayed; INTERFACE only if the decision is about the display/interaction.', ''),
 ('R5 A delegated item naming a topic without a value is coded by the concern of the topic (visual look → SPECIFIC-QUALITY, interaction capability).', ''), ('', ''),
 ('Worked examples (not to be coded):', 'h'),
 ('"Q: How long should sessions last? A: 30 minutes, then automatic logout"  →  OPTATIVE | INTERFACE | FUNCTIONAL | —', ''),
 ('"`gemini-flash` will remain available through demo week"  →  INDICATIVE | NA | NA | —', ''),
 ('"Use SQLite with WAL mode for local storage"  →  OPTATIVE | MACHINE | CONSTRAINT | Constraint: design & implementation', ''),
 ('"Expand component tests to cover reconnect and unread counts"  →  OPTATIVE | NA | PROJECT-PROCESS | —', ''),
]

def build(name):
    wb = Workbook(); g = wb.active; g.title = 'Guide'; g.column_dimensions['A'].width = 150
    for i, (txt, st) in enumerate(GUIDE, 1):
        c = g.cell(i, 1, txt); c.alignment = Alignment(wrap_text=True)
        c.font = Font(name=F, bold=bool(st), size=13 if st == 'h1' else 11 if st == 'h' else 10)
    ss = wb.create_sheet('Sessions'); ss.append(['Session', 'Date', 'Start (hh:mm)', 'End (hh:mm)', 'Last ID coded'])
    ss.append([1, '2026-10-26', '09:00', '10:15', 'V060'])  # example row
    for c in ss[1]: c.font = Font(name=F, bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='1F3864')
    for c in ss[2]: c.font = Font(name=F, italic=True, color='808080')
    ss.cell(2, 6, '← example, overwrite or delete').font = Font(name=F, italic=True, color='808080')
    for r in range(3, 13):
        for col in range(1, 6): ss.cell(r, col).fill = YEL; ss.cell(r, col).border = Border(top=thin, bottom=thin, left=thin, right=thin)
    for col, w in zip('ABCDEF', [9, 12, 13, 12, 14, 30]): ss.column_dimensions[col].width = w
    ws = wb.create_sheet('Annotate')
    ws.append(['ID', 'Decision text (as recorded)', 'Source link', 'D2 Mood', 'D3 Locus', 'D4 Concern', 'D4 Sub-code', 'Notes / doubts'])
    for c in ws[1]:
        c.font = Font(name=F, bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='1F3864'); c.alignment = Alignment(wrap_text=True, vertical='center')
    for d in S:
        ws.append([d['vid'], d['shown'], 'open', None, None, None, None, None])
        ws.cell(ws.max_row, 3).hyperlink = f"https://github.com/{d['repo']}/blob/HEAD/{d['file']}"
    for w, col in zip([7, 90, 8, 13, 13, 18, 32, 30], 'ABCDEFGH'): ws.column_dimensions[col].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.font = Font(name=F, color='0563C1', underline='single') if c.column == 3 else Font(name=F, size=10)
            c.alignment = Alignment(wrap_text=True, vertical='top'); c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
            if 4 <= c.column <= 8: c.fill = YEL
    ws.freeze_panes = 'B2'
    L = wb.create_sheet('Lists'); L.sheet_state = 'hidden'
    for i, v in enumerate(SUB, 1): L.cell(i, 1, v)
    n = len(S) + 1
    for col, opts in [('D', '"INDICATIVE,OPTATIVE"'), ('E', '"ENV,INTERFACE,MACHINE,NA"'),
                      ('F', '"FUNCTIONAL,PERFORMANCE,SPECIFIC-QUALITY,CONSTRAINT,PROJECT-PROCESS,NA"'), ('G', f'Lists!$A$1:$A${len(SUB)}')]:
        dv = DataValidation(type='list', formula1=opts, allow_blank=True); ws.add_data_validation(dv); dv.add(f'{col}2:{col}{n}')
    wb.active = 2; wb.save(f'../annotation/{name}')

build('validation_annotator_A.xlsx'); build('validation_annotator_B.xlsx')
