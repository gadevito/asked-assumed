"""Extract requirements decisions (codebook D1 provenance) from crawled artifacts -> data/decisions.jsonl"""
import json, re, glob, os, collections

def sections(text, level=r'#{2,3}'):
    """Yield (heading, body) for markdown headings of given levels."""
    hs = list(re.finditer(rf'^({level})\s+(.+?)\s*$', text, re.M))
    for i, h in enumerate(hs):
        end = len(text)
        for h2 in hs[i + 1:]:
            if len(h2.group(1)) <= len(h.group(1)): end = h2.start(); break
        yield h.group(2).strip(), text[h.end():end], len(h.group(1))

def flat_sections(text):
    """Yield (h2, heading, direct_body) for every ##/### heading; direct_body stops at the next heading of any level."""
    hs = list(re.finditer(r'^(#{2,4})\s+(.+?)\s*$', text, re.M)); h2 = ''
    for i, h in enumerate(hs):
        if len(h.group(1)) == 2: h2 = h.group(2).strip().lower()
        end = hs[i + 1].start() if i + 1 < len(hs) else len(text)
        yield h2, h.group(2).strip(), text[h.end():end]

def bullets(body):
    """Top-level list items (with continuation lines), skipping HTML comments and table rows."""
    body = re.sub(r'<!--.*?-->', '', body, flags=re.S)
    items, cur = [], None
    for line in body.splitlines():
        if re.match(r'^\s?(?:[-*+]|\d+[.)])\s+\S', line):
            if cur: items.append(cur)
            cur = re.sub(r'^\s?(?:[-*+]|\d+[.)])\s+', '', line).strip()
        elif cur is not None and line.strip() and not line.lstrip().startswith(('#', '|')):
            cur += ' ' + line.strip()
        elif not line.strip() and cur:
            items.append(cur); cur = None
    if cur: items.append(cur)
    return [i for i in items if len(i) > 3]

def table_rows(body):
    rows = [r for r in body.splitlines() if r.strip().startswith('|')]
    rows = [r for r in rows if not re.match(r'^\s*\|[\s:|-]+\|\s*$', r)]
    return [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows]

def D(rec, prov, text, section, file, **kw):
    return dict(tool=rec['tool'], repo=rec['repo'], file=file, section=section, provenance=prov, text=text.strip(), **kw)

def speckit(rec):
    out = []; f = rec['main']; t = rec['files'][f]
    for h, body, lvl in sections(t, r'##'):
        hl = h.lower()
        if hl.startswith('clarifications'):
            for line in body.splitlines():
                m = re.match(r'^\s*[-*]\s*Q:\s*(.*?)\s*→\s*A:\s*(.*)$', line)
                if m: out.append(D(rec, 'ASKED', m.group(1), h, f, answer=m.group(2)))
        elif re.match(r'assumptions?\b', hl):
            for b in bullets(body): out.append(D(rec, 'ASSUMED', b, h, f))
    for m in re.finditer(r'\[NEEDS CLARIFICATION:?\s*([^\]]*)\]', t):
        if 'auth method not specified' not in m.group(1):  # template example
            out.append(D(rec, 'OPEN', m.group(1) or '(unspecified)', 'inline marker', f))
    return out

_DEF = (r"you decide|(claude|agent|planner)'?s discretion|your call|claude[- ]decided|"
        r"let (claude|the agent|the planner|the model|you) decide|(claude|agent|planner) (picks|decides)\b")
DEFER = '(?i)' + _DEF
DEFER_START = re.compile(r'(?i)^[\W_]*(' + _DEF + ')')   # hand-back = the answer itself; "X → you decide; Y" is a partial detail
TICK = re.compile(r"(?i)[✓✔✅☑]|âœ“|:[a-z_]*check[a-z_]*:|^\s*(x|yes|y|\[x\]|\*|ok|check|selected|chosen|requested|user selected)\s*$|"
                  r"\(selected\)|user (chose|selected)|agent'?s pick|chosen by|^\s*\((refined|modified)\)\s*$")
REC = re.compile(r"(?i)\brecommended\b")
NOT_REC = re.compile(r"(?i)(not|counter-?|same as|than|into)\s*$")   # "not recommended", "Counter-recommended", "Same as recommended"
MATRIX = re.compile(r"(?i)^(sub-?decision|decision( point)?|area)s?$")   # one row per sub-decision, not per option

OTHER = re.compile(r"(?i)^\W*other\b")   # "Other (user-provided)", "Other: 2 LEDs": a slot for the developer's own text, not an agent option
META = re.compile(r'(?i)gray.?area|areas? (to )?discuss|which areas')   # GSD first asks which areas to discuss
CLOSING = re.compile(r"(?i)\bready (for|to write) (the )?context|\bwrite (the )?context|\bcreate context|"
                     r"explore (more|one more)( (gray|grey))? areas?|more (gray|grey) areas|enough\W+write|i'?m good\W+write")

def is_process_question(title, options):
    """Questions about the discussion itself, not about the system: which areas to discuss, and the closing
    "ready for context / explore more gray areas" prompt. Excluded from H3-H4."""
    return bool(META.search(title or '') or any(CLOSING.search(o) for o in options or []))

def _norm(s):
    return re.sub(r'[^a-z0-9]+', ' ', re.sub(r'(?i)\(recommended\)|\*\*|`', '', s).lower()).strip()

LABEL = re.compile(r"(?i)[(\[]\s*(also\s+)?recommended\b|[(\[][^)\]]*[,;]\s*recommended\s*[)\]]|"   # (Recommended), (Dify-style, Recommended)
                   r"(^|[.;:|—–\-*]\s*)recommended\s*([.:;!)\]—–\-*]|$|\s+for\b|\s+by\b)|"  # standalone tag, "Recommended for/by ..."
                   r"(?-i:\bRECOMMENDED\b)")                                             # upper-case tag
DESC_LABEL = re.compile(r"(?i)(^|[.!;]\s+)\**recommended\b|,\s*recommended\s*[.)]?\s*$")   # sentence-initial or trailing tag in a description
def is_rec(cells):
    """True if an option carries a recommendation LABEL (cells[0] = option name, the rest = description).
    "recommended" as ordinary content ("Recommended version only" as a name, "document recommended level") is not a label,
    nor are negated or comparative uses (check sheets v2-v4). In a description, a sentence starting with "Recommended" is one."""
    if any(DESC_LABEL.search(t) for t in cells[1:]): return True
    for t in cells:
        for m in LABEL.finditer(t):
            if not NOT_REC.search(t[:m.start() + len(m.group(0)) - len(m.group(0).lstrip(' .;:|—–-*([').lstrip())]): return True
    return False

def read_table(rows_all):
    """Header + option rows -> (rows, selected indexes, recommended indexes), or None for a matrix of sub-decisions.
    The option name is the column headed Option (first otherwise); the mark is read in the Selected column when the
    header has one (marks vary: ✓, x, yes, :white_check_mark:, ...), otherwise anywhere in the row."""
    head = rows_all[0]
    if MATRIX.match(head[0].strip()) or any(re.match(r'(?i)options\b', c.strip()) for c in head): return None
    nc = next((j for j, c in enumerate(head) if re.match(r'(?i)option\b', c.strip())), 0)
    order = lambda r: [r[nc]] + r[:nc] + r[nc + 1:] if nc < len(r) else r
    head = order(head); rows = [order(r) for r in rows_all[1:]]; rows = [r for r in rows if r and r[0]]
    col = next((j for j, c in enumerate(head) if re.search(r'(?i)select|chosen|pick', c)), None)
    def cell(r): return r[col] if col is not None and col < len(r) else ' '.join(r[1:])
    other_sel = any(OTHER.match(r[0]) and TICK.search(cell(r)) for r in rows)
    rows = [r for r in rows if not OTHER.match(r[0])]                    # Other rows are not options proposed by the agent
    sel = [i for i, r in enumerate(rows) if TICK.search(cell(r))]
    rec = [i for i, r in enumerate(rows) if is_rec(r[:col] if col is not None else r) and not re.search(DEFER, r[0])]
    return rows, sel, rec, other_sel

def match_choice(ch, rows):
    """Index of the single option named by a free-text User's choice, or None (exact/prefix match, else same first two words)."""
    c = _norm(ch)
    def opt(r):
        o = _norm(r[0]); return re.sub(r'^(option )?\(?[a-e1-9]\)?\s+', '', o) if len(o) > 3 else o
    hits = [i for i, r in enumerate(rows) if len(opt(r)) >= 3 and (c == opt(r) or c.startswith(opt(r) + ' ') or (len(c) >= 6 and opt(r).startswith(c)))]
    if not hits:
        w = c.split()[:2]
        hits = [i for i, r in enumerate(rows) if len(w) == 2 and len(' '.join(w)) >= 8 and opt(r).split()[:2] == w]
    return hits[0] if len(hits) == 1 else None
CHOICE = re.compile(r"\*\*User'?s? choice:?\*\*:?\s*(.*)")
HEADING = re.compile(r'^(#{2,6}\s+(.+)|\*\*(Q\d+[^*]*)\*\*.*)$')

def choice_items(text):
    """Read a GSD discussion log sequentially. Every option table is one decision; it takes the nearest preceding
    heading (## / ### / **Qn**) as title and the next "User's choice" line, if any, as answer. A "User's choice" with
    no pending table is a free-text decision. Returns (title, option rows, choice or None, raw text)."""
    items, cur, title, title_line, in_table = [], None, '', '', False
    for line in text.splitlines():
        h = HEADING.match(line.strip())
        if h:
            title = (h.group(2) or h.group(3) or '').strip(); title_line = line; in_table = False; continue
        if line.strip().startswith('|'):
            if not in_table:
                cur = {'title': title, 'table': [], 'choice': None, 'raw': [title_line] if title_line else []}
                items.append(cur); in_table = True
            cur['table'].append(line); cur['raw'].append(line); continue
        in_table = False
        m = CHOICE.search(line)
        if m:
            if cur is not None and cur['choice'] is None and cur['table']:
                cur['choice'] = m.group(1).strip(); cur['raw'].append(line)
            else:
                cur = {'title': title, 'table': [], 'choice': m.group(1).strip(), 'raw': [title_line, line] if title_line else [line]}
                items.append(cur)
            cur = None if cur['table'] else cur
    out = []
    for it in items:
        rows = table_rows('\n'.join(it['table']))
        if rows and not any(re.search(r'(?i)option|selected|choice', c) for c in rows[0]): continue   # not an option table
        rows = [rows[0]] + [r for r in rows[1:] if r and any(r)] if rows else []
        if not rows and it['choice'] is None: continue
        out.append((it['title'], rows, it['choice'], '\n'.join(it['raw']).strip()))
    return out

def gsd(rec):
    out = []
    for f, t in rec['files'].items():
        name = f.rsplit('/', 1)[-1]
        if 'DISCUSSION-LOG' in name:
            for title, rows_all, ch, raw in choice_items(t):
                tb = read_table(rows_all) if rows_all else ([], [], [], False)
                if tb is None: continue                                         # matrix of sub-decisions: not one question
                rows, sel_i, rec_i, other_sel = tb
                if not sel_i and ch and rows and not other_sel:                 # no tick: match the choice text
                    m = match_choice(ch, rows); sel_i = [m] if m is not None else []
                if ch is None: ch = ' / '.join(rows[i][0] for i in sel_i)   # choice recorded only by the tick
                sel_txt = ' '.join(rows[i][0] for i in sel_i)
                if DEFER_START.search(ch) or (sel_i and re.search(DEFER, sel_txt)): prov, beh = 'DELEGATED', 'DEFER-BACK'
                elif '[auto]' in ch.lower(): prov, beh = 'DELEGATED', 'AUTO'
                else:
                    prov = 'ASKED'
                    if not rows or not sel_i: beh = 'FREE'
                    elif not rec_i: beh = 'N/A'
                    else: beh = 'REC-ACCEPTED' if set(sel_i) & set(rec_i) else 'ALT-OPTION'
                out.append(D(rec, 'CHOICE-LOG', title, 'discussion-log', f, answer=ch, options=[r[0] for r in rows], n_options=len(rows),
                             n_selected=len(sel_i), sel_pos=sel_i, rec_pos=rec_i,
                             rec_in_choice=not rec_i and bool(re.search(r'(?i)\(recommended\)', ch)), behaviour=beh, log_provenance=prov, raw=raw))
        elif 'CONTEXT' in name:
            for h2, h, body in flat_sections(t):
                hl = h.lower()
                if 'discretion' in hl:
                    for b in bullets(body): out.append(D(rec, 'DELEGATED', b, h, f))
                elif h2.startswith('implementation decisions') or h2.startswith('decisions'):
                    for b in bullets(body):
                        if not re.match(r'(?i)none\b', b): out.append(D(rec, 'ASKED', b, h, f))
                elif 'deferred' in hl:
                    for b in bullets(body):
                        if not re.match(r'(?i)none\b', b): out.append(D(rec, 'OPEN', b, h, f))
        elif 'RESEARCH' in name:
            for h, body, lvl in sections(t):
                hl = h.lower()
                if hl.startswith('assumptions log'):
                    for r in table_rows(body)[1:]:
                        if len(r) >= 2 and r[1] and not r[1].startswith('['): out.append(D(rec, 'ASSUMED', r[1], h, f, risk=r[3] if len(r) > 3 else None))
                elif hl.startswith('open questions') and 'resolved' not in hl:
                    for b in bullets(body):
                        if re.match(r"(?i)\**\s*(what we know|what's unclear|what is unclear|recommendation|known|unknown|resolution)\b", b): continue
                        if not re.match(r'(?i)none', b): out.append(D(rec, 'OPEN', b, h, f))
    return out

def bmad(rec):
    out = []
    for f, t in rec['files'].items():
        name = f.rsplit('/', 1)[-1].lower()
        if name.endswith('.memlog.md') or name == 'memlog.md':
            for m in re.finditer(r'^\s*-\s*\((question|decision|assumption)\)\s*(.+)$', t, re.M):
                out.append(D(rec, {'question': 'OPEN', 'decision': 'SETTLED', 'assumption': 'ASSUMED'}[m.group(1)], m.group(2), 'memlog:' + m.group(1), f))
            continue
        idx_found = False
        for h, body, lvl in sections(t):
            hl = re.sub(r'^\d+\.\s*', '', h.lower())
            if hl.startswith('assumptions index') or (hl.startswith('assumptions') and name == 'spec.md'):
                idx_found = True
                for b in bullets(body) or [r[0] for r in table_rows(body)[1:] if r]: out.append(D(rec, 'ASSUMED', b, h, f))
            elif hl.startswith('open questions') and 'resolved' not in hl:
                for b in bullets(body) or [r[0] for r in table_rows(body)[1:] if r]:
                    if not re.match(r'(?i)none', b): out.append(D(rec, 'OPEN', b, h, f))
        if not idx_found:  # fall back to inline tags only if no index (avoid double counting)
            for m in re.finditer(r'\[ASSUMPTION:\s*([^\]]+)\]', t): out.append(D(rec, 'ASSUMED', m.group(1), 'inline tag', f))
    return out

if __name__ == '__main__':
    import sys
    if os.path.exists('data/decisions.jsonl') and '--force' not in sys.argv:
        sys.exit('data/decisions.jsonl is frozen: its IDs are referenced by the LLM codes and the annotation keys. '
                 'Re-extracting changes IDs. Use --force only to rebuild the whole pipeline from scratch.')
    F = {'speckit': speckit, 'gsd': gsd, 'bmad': bmad}
    allx = []; units = collections.Counter(); empty = collections.Counter()
    for fn in sorted(glob.glob('data/artifacts/*/*.json')):
        rec = json.load(open(fn))
        if 'main' not in rec: continue
        units[rec['tool']] += 1
        ds = F[rec['tool']](rec)
        if not ds: empty[rec['tool']] += 1
        for i, d in enumerate(ds): d['id'] = f"{rec['tool']}:{rec['repo']}:{i}"
        allx += ds
    with open('data/decisions.jsonl', 'w') as f:
        for d in allx: f.write(json.dumps(d, ensure_ascii=False) + '\n')
    print('units', dict(units), 'units without decisions', dict(empty))
    c = collections.Counter((d['tool'], d['provenance']) for d in allx)
    for t in F: print(t, {p: c[(t, p)] for p in ['ASKED', 'DELEGATED', 'ASSUMED', 'OPEN', 'SETTLED', 'CHOICE-LOG']})
    g = [d for d in allx if d.get('behaviour')]
    print('GSD behaviour', collections.Counter(d['behaviour'] for d in g))
