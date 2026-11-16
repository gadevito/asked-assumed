"""Pilot figures for H3 (option order), H4 (recommendation label), and the agent-answered diagnostic.
Attribution, exclusions, and the H4 test come from rq3_pools.py, shared with power_sim.py and the confirmatory analysis."""
import json, random, collections, statistics as st, numpy as np
from rq3_pools import pools, h4_arrays, h4_test, AUTO_ANS, single

B = [json.loads(l) for l in open('data/rq3_blocks.jsonl')]
P = pools(B); hum, unl, h4, auto = P['hum'], P['unl'], P['h4'], P['auto']
print('excluded: automatic answers outside --auto mode',
      sum(1 for b in B if b['log_provenance'] == 'ASKED' and not b['auto_mode'] and single(b) and AUTO_ANS.search(b['answer'] or '')))
print('excluded: "(Recommended)" only in the User\'s choice', sum(1 for b in hum if b.get('rec_in_choice')))

first = sum(b['sel_pos'][0] == 0 for b in unl); ref = st.mean(1 / b['n_options'] for b in unl)
print(f"H3  unlabelled single-choice questions {len(unl)} in {len({b['repo'] for b in unl})} repos: "
      f"first option {first}/{len(unl)} = {first/len(unl):.1%}, uniform reference mean 1/k = {ref:.1%}")

repos, U, H, S = h4_arrays(unl, h4)
r = h4_test(U, H, S, B=10_000, rng=np.random.default_rng(20261110))
hit = int(S.sum()); n = r['n']
print(f"H4  recommended option not first {n} in {len({b['repo'] for b in h4})} repos (dropped for <20 comparators: "
      f"{len(P['h4_all']) - n}): chosen {hit} = {hit/n:.1%}, expected {hit - r['stat']*n:.1f} = {hit/n - r['stat']:.1%}; "
      f"one-sided bootstrap p = {r['p']:.4f} (discarded replicates {r['discarded']})")

lab = [b for b in hum if b['rec_pos']]
f1 = sum(b['rec_pos'][0] == 0 for b in lab)
print(f"    labelled questions with recommended listed first: {f1}/{len(lab)} = {f1/len(lab):.1%}")

per = collections.defaultdict(list)
for b in auto: per[b['repo']].append(b['sel_pos'][0] == 0)
reps = list(per); rnd = random.Random(1); bs = []
for _ in range(10_000):
    s = [x for rp in (rnd.choice(reps) for _ in reps) for x in per[rp]]; bs.append(sum(s) / len(s))
bs.sort(); fa = sum(sum(v) for v in per.values())
print(f"DIAG agent-answered questions {len(auto)} in {len(reps)} repos: first option {fa}/{len(auto)} = {fa/len(auto):.1%} "
      f"(95% cluster-bootstrap CI {bs[250]:.2f}-{bs[9750]:.2f})")
