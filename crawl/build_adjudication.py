"""Adjudication workbook: validation decisions where A and B disagree on at least one dimension.
Both codings shown side by side; the agreed codes are entered jointly. LLM codes are not shown."""
import json, sys
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from agreement import read_xlsx, DIMS

ANN = '../annotation'
key = {k['vid']: k for k in json.load(open(f'{ANN}/validation_key.json'))}
A = read_xlsx(f'{ANN}/validation_annotator_A.xlsx'); B = read_xlsx(f'{ANN}/validation_annotator_B.xlsx')
dis = [i for i in sorted(key) if any(A[i][d] != B[i][d] for d in DIMS)]
SUB = [r[0].value for r in load_workbook(f'{ANN}/validation_annotator_A.xlsx')['Lists'].iter_rows()]
F = 'Arial'; thin = Side(style='thin', color='BFBFBF'); YEL = PatternFill('solid', fgColor='FFF2CC'); RED = Font(name=F, size=10, bold=True, color='C00000')
wb = Workbook(); g = wb.active; g.title = 'Guide'; g.column_dimensions['A'].width = 140
for i, t in enumerate(['Adjudication — validation sample (codebook v0.3)', '',
    f'{len(dis)} decisions on which A and B disagree on at least one dimension. Codes that differ are shown in red.',
    'Discuss each decision together, with the codebook at hand, and enter the agreed codes in the yellow cells (all four, also where you already agreed).',
    'Use the Rationale column to record which rule or definition settled the case; these notes feed the paper\'s discussion of boundary cases.',
    'If a case cannot be settled by the codebook, write UNRESOLVED in the Rationale column and pick the closer reading.'], 1):
    c = g.cell(i, 1, t); c.font = Font(name=F, bold=(i == 1), size=13 if i == 1 else 10); c.alignment = Alignment(wrap_text=True)
ws = wb.create_sheet('Adjudicate')
H = ['ID', 'Decision text', 'Link'] + [f'A {d}' for d in DIMS] + [f'B {d}' for d in DIMS] + ['A notes', 'B notes'] + [f'Agreed {d}' for d in DIMS] + ['Rationale']
ws.append(H)
for c in ws[1]: c.font = Font(name=F, bold=True, color='FFFFFF'); c.fill = PatternFill('solid', fgColor='1F3864'); c.alignment = Alignment(wrap_text=True)
for i in dis:
    ws.append([i, key[i]['shown'], 'open'] + [A[i][d] for d in DIMS] + [B[i][d] for d in DIMS] + [A[i]['note'], B[i]['note']] + [None] * 5)
    r = ws.max_row; ws.cell(r, 3).hyperlink = f"https://github.com/{key[i]['repo']}/blob/HEAD/{key[i]['file']}"
widths = [6, 60, 6] + [12, 11, 15, 22] * 2 + [30, 30] + [13, 12, 16, 24, 35]
for n, w in enumerate(widths, 1): ws.column_dimensions[ws.cell(1, n).column_letter].width = w
for row in ws.iter_rows(min_row=2):
    for c in row:
        c.alignment = Alignment(wrap_text=True, vertical='top'); c.border = Border(top=thin, bottom=thin, left=thin, right=thin)
        c.font = Font(name=F, color='0563C1', underline='single') if c.column == 3 else Font(name=F, size=10 if c.column != 2 else 9)
        if c.column >= 14: c.fill = YEL
    for j, d in enumerate(DIMS):
        if row[3 + j].value != row[7 + j].value: row[3 + j].font = RED; row[7 + j].font = RED
ws.freeze_panes = 'D2'
L = wb.create_sheet('Lists'); L.sheet_state = 'hidden'
for n, v in enumerate(SUB, 1): L.cell(n, 1, v)
m = len(dis) + 1
for col, opts in [('N', '"INDICATIVE,OPTATIVE"'), ('O', '"ENV,INTERFACE,MACHINE,NA"'),
                  ('P', '"FUNCTIONAL,PERFORMANCE,SPECIFIC-QUALITY,CONSTRAINT,PROJECT-PROCESS,NA"'), ('Q', f'Lists!$A$1:$A${len(SUB)}')]:
    dv = DataValidation(type='list', formula1=opts, allow_blank=True); ws.add_data_validation(dv); dv.add(f'{col}2:{col}{m}')
wb.active = 1; wb.save(f'{ANN}/validation_adjudication.xlsx'); print('adjudication items', len(dis))
