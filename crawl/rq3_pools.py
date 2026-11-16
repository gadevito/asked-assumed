"""Shared definitions for RQ3 (H3, H4, diagnostic): attribution of answers, exclusions, and the H4 test.
Used unchanged by the pilot figures (rq3_presentation.py), the power/calibration simulation (power_sim.py),
and the confirmatory analysis, so that the simulated test is the pre-registered one."""
import re, collections, numpy as np
from extract import DEFER, is_process_question

# ---------- attribution and exclusions (Analysis Plan: "Attribution of answers", "Exclusions") ----------
AUTO_ANS = re.compile(r"(?i)^[\W_]*(auto[- ]?(selected|picked|chosen|accepted|resolved|decided)\b|\(auto\)|auto[- ]mode\b)")

def auto_answered(b):
    """Answer recorded as the agent's: auto-mode log, [auto] tag, or an answer saying the agent chose it."""
    return b['auto_mode'] or (b['log_provenance'] != 'ASKED' and b['behaviour'] == 'AUTO') or bool(AUTO_ANS.search(b['answer'] or ''))

def single(b):
    """One listed option chosen; not a process question; not the hand-back option."""
    return (b['n_options'] >= 2 and len(b['sel_pos']) == 1 and not is_process_question(b['text'], b['options'])
            and not re.search(DEFER, b['options'][b['sel_pos'][0]]))

def pools(blocks):
    """Developer-answered single-choice questions (hum), unlabelled comparators (unl), H4 questions with the
    recommended option not first and k having enough comparators (h4), agent-answered questions (auto)."""
    hum = [b for b in blocks if b['log_provenance'] == 'ASKED' and not auto_answered(b) and single(b)]
    unl = [b for b in hum if not b['rec_pos'] and not b.get('rec_in_choice')]
    h4_all = [b for b in hum if len(b['rec_pos']) == 1 and b['rec_pos'][0] != 0]
    auto = [b for b in blocks if auto_answered(b) and single(b)]
    return dict(hum=hum, unl=unl, h4=eligible_h4(unl, h4_all), h4_all=h4_all, auto=auto)

# ---------- H4 test (Analysis Plan, H4) ----------
KMAX, MIN_COMP = 8, 20          # k capped at 8 for indexing; a k needs >= 20 unlabelled comparators

def eligible_h4(unl, h4):
    """H4 questions whose k has >= MIN_COMP unlabelled comparators in the observed data."""
    c = collections.Counter(min(b['n_options'], KMAX) for b in unl)
    return [b for b in h4 if c[min(b['n_options'], KMAX)] >= MIN_COMP]

def h4_arrays(unl, h4):
    """Per-repository arrays over the union of repositories, so that a repository contributing comparators and
    H4 questions is resampled as one unit. U[r,k,p]: unlabelled questions with k options where position p was
    chosen; H[r,k,p]: H4 questions with k options and recommended option at p; S[r]: H4 selections of it."""
    repos = sorted({b['repo'] for b in unl} | {b['repo'] for b in h4}); ix = {r: i for i, r in enumerate(repos)}
    U = np.zeros((len(repos), KMAX + 1, KMAX)); H = np.zeros_like(U); S = np.zeros(len(repos))
    for b in unl: U[ix[b['repo']], min(b['n_options'], KMAX), min(b['sel_pos'][0], KMAX - 1)] += 1
    for b in h4:
        H[ix[b['repo']], min(b['n_options'], KMAX), min(b['rec_pos'][0], KMAX - 1)] += 1
        S[ix[b['repo']]] += b['sel_pos'][0] == b['rec_pos'][0]
    return repos, U, H, S

def _stat(Usum, Hsum, Ssum):
    """(O - E) / n, where E uses the positional baseline P(position | k) of the comparators. Works on batches."""
    tot = Usum.sum(-1, keepdims=True); P = np.divide(Usum, tot, out=np.zeros_like(Usum), where=tot > 0)
    n = Hsum.sum((-2, -1))
    return (Ssum - (P * Hsum).sum((-2, -1))) / np.where(n > 0, n, 1), n, tot[..., 0]

def h4_test(U, H, S, B=10_000, rng=None):
    """One-sided p = (1 + #{replicates with statistic <= 0}) / (B_used + 1), from a cluster bootstrap that resamples
    repositories with all their questions and re-estimates the baseline in every replicate. Replicates in which
    a k used by H4 has fewer than MIN_COMP comparators, or that contain no H4 question, are discarded and counted."""
    rng = rng or np.random.default_rng()
    obs, n, _ = _stat(U.sum(0), H.sum(0), S.sum())
    used_k = H.sum((0, 2)) > 0
    R = U.shape[0]; W = rng.multinomial(R, np.full(R, 1 / R), size=B).astype(float)        # B x R repository weights
    st, nb, totb = _stat(np.einsum('br,rkp->bkp', W, U), np.einsum('br,rkp->bkp', W, H), W @ S)
    bad = ((totb < MIN_COMP) & used_k[None, :]).any(1) | (nb == 0)
    st = st[~bad]
    return dict(stat=float(obs), n=int(n), p=float((1 + (st <= 0).sum()) / (len(st) + 1)), discarded=int(bad.sum()))
