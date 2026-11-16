"""Units whose GSD context was settled by the agent rather than the developer (RQ2 / H2).

A GSD unit (phase) is AUTO-SETTLED if
  (a) the header of its CONTEXT.md or DISCUSSION-LOG.md (first 800 characters) declares an automatic mode:
      a "Mode:" or "Gathered:" line mentioning --auto, auto-selected/accepted/generated, autonomous, or yolo; or
  (b) its discussion log records at least one answer and every answer is attributed to the agent
      (rq3_pools.auto_answered: auto-mode log, [auto] tag, or "Auto-selected ...").
Mentions of these words elsewhere in the document (configuration prose, feature content) do not count.
Decisions of auto-settled units recorded under Implementation Decisions are kept apart from the developer-answered
group: they are neither ASKED nor DELEGATED (authorizing an automatic mode is not delegating a single decision)."""
import json, glob, re
from extract import choice_items, read_table, CHOICE
from rq3_pools import AUTO_ANS

HEADER_MODE = re.compile(r"(?im)^\W*(mode|gathered)\W.{0,120}?(--auto\b|auto[- ]?(selected|accepted|generated)|autonomous|\byolo\b)")

def answers_all_agent(log_text):
    ch = [m.group(1).strip() for m in CHOICE.finditer(log_text)]
    hdr_auto = bool(re.search(r"(?i)\*\*Mode:?\*\*:?\s*`?--auto", log_text[:800]))
    return len(ch) > 0 and (hdr_auto or all(AUTO_ANS.search(c) or '[auto]' in c.lower() for c in ch))

def auto_settled(files):
    """files: {path: text} of one GSD unit -> (bool, reason)."""
    for fn, t in files.items():
        n = fn.rsplit('/', 1)[-1]
        if ('CONTEXT' in n or 'DISCUSSION-LOG' in n):
            m = HEADER_MODE.search(t[:800])
            if m: return True, f'{n}: {m.group(0).strip()[:120]}'
    for fn, t in files.items():
        if 'DISCUSSION-LOG' in fn.rsplit('/', 1)[-1] and answers_all_agent(t):
            return True, f'{fn.rsplit("/", 1)[-1]}: every answer attributed to the agent'
    return False, ''

def auto_units(path='data/artifacts/gsd/*.json'):
    out = {}
    for g in glob.glob(path):
        rec = json.load(open(g))
        ok, why = auto_settled(rec['files'])
        if ok: out[rec['repo']] = why
    return out

if __name__ == '__main__':
    import collections
    d = [json.loads(l) for l in open('data/decisions.jsonl')]
    c = collections.Counter((x['repo'], x['provenance']) for x in d if x['tool'] == 'gsd')
    U = auto_units()
    print(f"auto-settled GSD units: {len(U)}; ASKED records in them: {sum(c[(r, 'ASKED')] for r in U)}; "
          f"DELEGATED: {sum(c[(r, 'DELEGATED')] for r in U)}")
    for r, why in sorted(U.items()): print(f"- {r} | ASKED {c[(r, 'ASKED')]} | {why}")
    json.dump(U, open('../results/gsd_auto_units.json', 'w'), indent=1, ensure_ascii=False)
