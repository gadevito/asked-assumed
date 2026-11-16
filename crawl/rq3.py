"""RQ3: acceptance of the agent's recommended option in GSD discussion logs -> data/rq3_blocks.jsonl"""
import json, collections, re, statistics as st
from extract import gsd, is_process_question
from lang import english

logs = [json.loads(l) for l in open('data/gsdlogs.jsonl')]
blocks = []
for lg in logs:
    rec = {'tool': 'gsd', 'repo': lg['repo'], 'files': {lg['path']: lg['text']}}
    for d in gsd(rec):
        if d['provenance'] == 'CHOICE-LOG':
            d['auto_mode'] = '--auto' in lg['text'] or 'Mode:** `--auto`' in lg['text']
            blocks.append(d)
with open('data/rq3_blocks.jsonl', 'w') as f:
    for b in blocks: f.write(json.dumps(b, ensure_ascii=False) + '\n')

print('logs', len(logs), 'repos', len({l['repo'] for l in logs}), 'blocks', len(blocks))
print('behaviour (all):', collections.Counter(b['behaviour'] for b in blocks))
from extract import META
meta = [b for b in blocks if META.search(b['text'] or '')]
multi = [b for b in blocks if not META.search(b['text'] or '') and b.get('n_selected', 0) > 1]
print('excluded: area-selection questions', len(meta), '| multi-select answers', len(multi))
print('excluded: closing "ready for context" questions', sum(1 for b in blocks if not META.search(b['text'] or '') and is_process_question(b['text'], b['options'])))
human = [b for b in blocks if b['log_provenance'] == 'ASKED' and not b['auto_mode'] and not is_process_question(b['text'], b['options']) and b.get('n_selected', 0) <= 1]
rec = [b for b in human if b['behaviour'] in ('REC-ACCEPTED', 'ALT-OPTION')]
print('human-answered blocks', len(human), '| with recommended marked and a selection', len(rec),
      '| repos', len({b['repo'] for b in rec}))
acc = sum(b['behaviour'] == 'REC-ACCEPTED' for b in rec)
print(f'pooled acceptance: {acc}/{len(rec)} = {acc/len(rec):.1%}')
per = collections.defaultdict(list)
for b in rec: per[b['repo']].append(b['behaviour'] == 'REC-ACCEPTED')
rates = [sum(v)/len(v) for v in per.values()]
print(f'per-repo acceptance: median {st.median(rates):.0%}, mean {st.mean(rates):.1%}, repos at 100%: {sum(r==1 for r in rates)}/{len(rates)}')
