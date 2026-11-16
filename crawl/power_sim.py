"""Power and type-I error of the pre-registered tests, simulated on pilot data.

H1: exact one-sided sign test on NASM - NASK per specification (ties dropped).
H4: the pre-registered test itself (rq3_pools.h4_test: cluster bootstrap with B = 10,000, repositories resampled with
all their questions, baseline re-estimated per replicate, k with >= 20 comparators). Each simulated confirmatory
corpus resamples pilot repositories (with all their questions) until it holds TARGET H4 questions; all unlabelled
questions of the corpus serve as comparators, as in the protocol. H4 outcomes are then regenerated:
  null:        P(select) = pilot positional baseline P(position | k);
  alternative: P(select) = p1.
Repository heterogeneity: a latent per-repository quantile u_r ~ U(0,1) gives each question q = BetaPPF(u_r; mean, ICC),
so outcomes in a repository are correlated with intra-class correlation ICC (pilot estimate 0.56).
alpha = 0.0125 (Bonferroni worst case of Holm over four hypotheses). Monte Carlo standard errors are reported."""
import json, os, sys, numpy as np
from multiprocessing import Pool
from scipy.stats import binom, beta as betad
from rq3_pools import pools, h4_arrays, h4_test, KMAX

ALPHA, TARGET, SIMS, B = 0.0125, 60, int(os.environ.get('SIMS', 500)), 10_000

# ---------- H1 ----------
def sign_power(n_specs, p_tie, theta, sims=20000, rng=np.random.default_rng(1)):
    m = rng.binomial(n_specs, 1 - p_tie, sims); pw = 0
    for mm in np.unique(m):
        crit = min(k for k in range(mm + 1) if binom.sf(k - 1, mm, 0.5) <= ALPHA)
        pw += (m == mm).sum() * binom.sf(crit - 1, mm, theta)
    return pw / sims

# ---------- H4 ----------
P = pools([json.loads(l) for l in open('data/rq3_blocks.jsonl')])
REPOS, U, H, S = h4_arrays(P['unl'], P['h4'])
NH = H.sum((1, 2))                                                     # H4 questions per repository
BASE = np.divide(U.sum(0), U.sum(0).sum(-1, keepdims=True), out=np.zeros(U.shape[1:]), where=U.sum(0).sum(-1, keepdims=True) > 0)

def draw_q(mean, icc, u):
    if icc <= 0: return np.full_like(u, mean, dtype=float)
    a, b = mean * (1 - icc) / icc, (1 - mean) * (1 - icc) / icc
    return betad.ppf(u, a, b)

def one(args):
    seed, scenario, p1, icc = args
    rng = np.random.default_rng(seed); idx = []; nh = 0
    while nh < TARGET:
        j = rng.integers(len(REPOS)); idx.append(j); nh += NH[j]
    idx = np.array(idx); Us, Hs = U[idx], H[idx]; Ss = np.zeros(len(idx))
    u = rng.random(len(idx))
    for i in range(len(idx)):
        ks, ps = np.nonzero(Hs[i])
        for k, p in zip(ks, ps):
            m = BASE[k, p] if scenario == 'null' else p1
            q = draw_q(m, icc, np.array([u[i]]))[0]
            Ss[i] += rng.binomial(int(Hs[i, k, p]), q)
    return h4_test(Us, Hs, Ss, B=B, rng=rng)['p'] <= ALPHA

if __name__ == '__main__':
    print('H1 sign test, 150 specs, tie rate 0.21 (pilot 31/148): power',
          {th: round(sign_power(150, 0.21, th), 3) for th in (0.60, 0.65, 0.70, 0.85)})
    print(f'pilot: {len(P["h4"])} H4 questions in {int((NH > 0).sum())} repos; {len(P["unl"])} comparators in {len(REPOS)} repos; '
          f'target {TARGET} H4 questions; {SIMS} simulations per scenario; B = {B}', flush=True)
    scen = [('null', None, icc) for icc in (0.0, 0.2, 0.56)] + [('alt', p1, icc) for icc in (0.2, 0.56) for p1 in (0.25, 0.30, 0.40)]
    with Pool(max(1, os.cpu_count() - 1)) as pool:
        for k, (sc, p1, icc) in enumerate(scen):
            rej = pool.map(one, [(1000 * k + s, sc, p1, icc) for s in range(SIMS)])
            r = np.mean(rej); se = np.sqrt(r * (1 - r) / SIMS)
            what = 'type-I error' if sc == 'null' else f'power at p1={p1}'
            print(f'H4 {what:18s} ICC={icc:<4}: {r:.3f} (MC s.e. {se:.3f})', flush=True)
