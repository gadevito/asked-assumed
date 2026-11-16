"""RQ3 extractor check: sample of GSD discussion-log blocks with the parser's output, for manual verification.
Usage: python build_rq3_check.py VERSION SEED   (repositories used in earlier check sheets are excluded)"""
import json, random, re, collections, sys, glob
VER, SEED = (sys.argv[1], int(sys.argv[2])) if len(sys.argv) > 2 else ('v2', 20261025)
PREV = {k['repo'] for f in glob.glob('../annotation/rq3_check*_key.json') if VER not in f for k in json.load(open(f))}
META = re.compile(r'(?i)gray.?area|areas? (to )?discuss|which areas')
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation

B = [json.loads(l) for l in open('data/rq3_blocks.jsonl')]
logs = {(d['repo'], d['path']): d['text'] for d in map(json.loads, open('data/gsdlogs.jsonl'))}
QUOTA = {'REC-ACCEPTED': 20, 'ALT-OPTION': 15, 'FREE': 10, 'N/A': 10, 'DEFER-BACK': 5}
rnd = random.Random(SEED); S = []
for beh, n in QUOTA.items():
    pool = [b for b in B if b['behaviour'] == beh and not b['auto_mode']]; rnd.shuffle(pool); used = set()
    for b in pool:
        if b['repo'] in used or b['repo'] in PREV: continue
        if META.search(b['text'] or '') or b.get('n_selected', 0) > 1 or len(b['raw']) > 3000: continue
        used.add(b['repo']); S.append(b)
        if sum(1 for x in S if x['behaviour'] == beh) == n: break
rnd.shuffle(S)
LABEL = {'REC-ACCEPTED': 'recommended option chosen', 'ALT-OPTION': 'another listed option chosen', 'FREE': 'free answer / no option ticked',
         'N/A': 'no option marked as recommended', 'DEFER-BACK': 'human handed the choice back ("you decide")'}
F = 'Arial'; thin = Side(style='thin', color='BFBFBF'); YEL = PatternFill('solid', fgColor='FFF2CC')
wb = Workbook(); g = wb.active; g.title = 'Guide'; g.column_dimensions['A'].width = 140
for i, t in enumerate([
    f'RQ3 extractor check {VER} — GSD discussion logs (one question per row)', '',
    'Each row shows one decision block from a GSD DISCUSSION-LOG.md and what the extraction script read from it.',
    'For each row, compare the block (column B) with the script output (columns C–D) and answer in the yellow cells:',
    '  E  Is the reading correct?  YES / NO',
    '  F  If NO, the correct reading (choose from the list).',
    '  G  Notes (optional).', '',
    'How to decide the correct reading — apply these steps in order and stop at the first that applies:',
    '  1. HANDED BACK: the User\'s choice (or the marked option) leaves the decision to the agent, e.g. "You decide", "Claude\'s discretion", '
    '"Claude-decided", "Let the planner decide" -> human handed the choice back ("you decide"). This holds even if another option is also marked.',
    '  2. NO LISTED OPTION CHOSEN: no option is marked AND the User\'s choice does not name a listed option (or there is no User\'s choice) '
    '-> free answer / no option ticked.',
    '  3. NO RECOMMENDATION LABEL: no option is labelled as recommended -> no option marked as recommended (whatever was chosen).',
    '  4. Otherwise: the chosen option is the recommended one -> recommended option chosen; else -> another listed option chosen.', '',
    'CHOSEN option = the option with ANY mark in the Selected column (✓, x, yes, :white_check_mark:, ...). If no option is marked, the option '
    'that the User\'s choice names, even with slightly different wording (e.g. "Google Colab (Recommended)" names "Google Colab").',
    'RECOMMENDED label = the agent explicitly labels that option as recommended: "(Recommended)" in the name, or "Recommended" / "RECOMMENDED" / '
    '"Recommended for ..." in its description. Words such as "recommends" or "recommendation" describing something else '
    '(e.g. "Claude recommends the leanest option" in a You-decide row, "No recommendation") are NOT a label.',
    'A "You decide" row is never the recommended option.', '',
    'Additional rules (final):',
    '  - EXCLUDE: if the developer chose several options at once (e.g. "All of them") write NO in E, leave F empty, and write "EXCLUDE: multi-select" in G.',
    '    If the table lists several sub-decisions, one per row (headers such as Decision / Sub-decision / Options considered), write NO, leave F empty, and "EXCLUDE: matrix".',
    '  - CHOSEN marks: any positive indication in the Selected column counts (✓, x, yes, :white_check_mark:, requested, (selected), user selected, ✓ (modified)). '
    'Negative ones do not (no, rejected, ❌, deferred, —).',
    '  - CHOICE IN WORDS: with no mark, the option that the User\'s choice clearly describes, even reworded or with extra detail; if it describes something not listed -> free answer.',
    '  - RECOMMENDED must be IN THE TABLE (name or description of an option). Not a label: "(Recommended)" only in the User\'s choice; '
    '"not recommended", "Counter-recommended", "Same as recommended"; the words "recommends" / "recommendation".',
    '  - HANDED BACK only if the answer to the question itself is left to the agent ("You decide", "Agent decides -> ...", "Claude-decided", '
    'or the You-decide row is marked). If the developer picks an option and leaves only a detail to the agent, it is not handed back.',
    '  - Tables not in English: same rules.',
    '  - OTHER: if the marked row is an "Other" option holding text written by the developer (e.g. "Other (user-provided)", "Other: 2 LEDs"), '
    'it is not an option proposed by the agent -> free answer / no option ticked.',
    '  - "(refined)" and "(modified)" in the Selected column count as marks.', '',
    'Work alone: do not discuss rows with the other annotator until both sheets are returned.',
    'Example: options A (Recommended) ✓ and B, User\'s choice: A  ->  script says "recommended option chosen"  ->  E = YES.']):
    c = g.cell(i + 1, 1, t); c.font = Font(name=F, bold=(i == 0), size=13 if i == 0 else 10); c.alignment = Alignment(wrap_text=True)
ws = wb.create_sheet('Check')
ws.append(['ID', 'Decision block (as recorded)', 'Script reading', 'Options found', 'Correct? (YES/NO)', 'If NO: correct reading', 'Notes'])
for c in ws[1]: c.font = Font(name=F, bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='1F3864'); c.alignment = Alignment(wrap_text=True)
key = []
for i, b in enumerate(S, 1):
    rid = f'Q{i:02d}'; key.append({'qid': rid, 'repo': b['repo'], 'file': b['file'], 'behaviour': b['behaviour'], 'title': b['text']})
    ws.append([rid, b['raw'], LABEL[b['behaviour']], b['n_options'], None, None, None])
for w, col in zip([6, 95, 26, 9, 12, 30, 30], 'ABCDEFG'): ws.column_dimensions[col].width = w
for row in ws.iter_rows(min_row=2):
    for c in row:
        c.font = Font(name=F, size=9 if c.column == 2 else 10); c.alignment = Alignment(wrap_text=True, vertical='top')
        c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
        if c.column >= 5: c.fill = YEL
ws.freeze_panes = 'C2'
L = wb.create_sheet('Lists'); L.sheet_state = 'hidden'
for i, v in enumerate(LABEL.values(), 1): L.cell(i, 1, v)
n = len(S) + 1
dv = DataValidation(type='list', formula1='"YES,NO"', allow_blank=True); ws.add_data_validation(dv); dv.add(f'E2:E{n}')
dv = DataValidation(type='list', formula1=f'Lists!$A$1:$A${len(LABEL)}', allow_blank=True); ws.add_data_validation(dv); dv.add(f'F2:F{n}')
wb.active = 1; wb.save(f'../annotation/rq3_extractor_check_{VER}.xlsx')
json.dump(key, open(f'../annotation/rq3_check_{VER}_key.json', 'w'), indent=1, ensure_ascii=False)
print('blocks', len(S), collections.Counter(b['behaviour'] for b in S))
