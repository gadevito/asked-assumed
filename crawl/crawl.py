"""Full crawler: SDD artifacts (Spec Kit, GSD, BMAD) for 'Asked or Assumed' study.
Stages (resumable, cached under data/):
  1 search   -> data/candidates_<tool>.jsonl   (code-search hits, sharded by size)
  2 enrich   -> data/repos.json                (repo metadata + commit count), random order, until N_PASS pass filters
  3 fetch    -> data/artifacts/<tool>/<owner__repo>.json (one unit per repo: main file + siblings + file history)
"""
import os, sys, json, time, random, re, urllib.request, urllib.parse, urllib.error, hashlib
TOK = os.environ['GITHUB_TOKEN']
D = 'data'; os.makedirs(D, exist_ok=True)
SEED = 20261019; N_PASS = 150   # sample 150 per tool (100 target + reserve)
SHARDS = ['size:<2000','size:2000..3999','size:4000..5999','size:6000..7999','size:8000..10999',
          'size:11000..14999','size:15000..19999','size:20000..29999','size:>=30000']
TOOLS = {
 'speckit': {'q': '"# Feature Specification" "**Feature Branch**" filename:spec.md path:specs',
             'unit': 'file'},
 'gsd':     {'q': '"## Implementation Decisions" path:.planning/phases filename:CONTEXT.md',
             'unit': 'dir'},
 'bmad':    {'q': ['"Assumptions Index" path:_bmad-output filename:prd.md',
                   '"## Assumptions" "## Open Questions" path:_bmad-output filename:SPEC.md'],
             'unit': 'dir'},
}
def log(*a): print(time.strftime('%H:%M:%S'), *a, flush=True)
def req(url, accept='application/vnd.github+json', raw=False):
    for attempt in range(8):
        try:
            r = urllib.request.Request(url, headers={'Authorization': f'Bearer {TOK}', 'Accept': accept,
                                                     'User-Agent': 'refsq-asked-assumed', 'X-GitHub-Api-Version': '2022-11-28'})
            with urllib.request.urlopen(r, timeout=40) as resp:
                body = resp.read(); return (body if raw else json.loads(body)), resp.headers
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                ra = e.headers.get('Retry-After'); reset = e.headers.get('X-RateLimit-Reset')
                wait = int(ra) if ra else max(5, int(reset) - int(time.time()) + 2) if reset and e.headers.get('X-RateLimit-Remaining') == '0' else 30 * (attempt + 1)
                log('rate-limited, sleep', wait); time.sleep(min(wait, 900)); continue
            if e.code in (404, 409, 451): return None, None
            if e.code >= 500: time.sleep(10); continue
            raise
        except Exception as e:
            log('net err', e); time.sleep(10)
    return None, None

def stage_search(tool):
    out = f'{D}/candidates_{tool}.jsonl'
    if os.path.exists(out): log(tool, 'search cached'); return
    seen = {}; qs = TOOLS[tool]['q']; qs = [qs] if isinstance(qs, str) else qs
    for q, sh in [(q, sh) for q in qs for sh in SHARDS]:
        for page in range(1, 11):
            d, _ = req('https://api.github.com/search/code?' + urllib.parse.urlencode({'q': f'{q} {sh}', 'per_page': 100, 'page': page}))
            time.sleep(6.5)
            if not d or not d.get('items'): break
            for it in d['items']:
                k = (it['repository']['full_name'], it['path'])
                seen[k] = {'repo': k[0], 'path': k[1], 'sha': it['sha'], 'fork': it['repository'].get('fork')}
            log(tool, sh, 'p', page, 'total', d['total_count'], 'collected', len(seen))
            if len(d['items']) < 100: break
    with open(out, 'w') as f:
        for v in seen.values(): f.write(json.dumps(v) + '\n')
    log(tool, 'candidates', len(seen), 'repos', len({v['repo'] for v in seen.values()}))

TEMPLATE_NAME = re.compile(r'(?i)(spec-?kit|get-shit-done|bmad|template|boilerplate|starter|example|demo|tutorial|sample|playground)')
def commit_count(repo):
    d, h = req(f'https://api.github.com/repos/{repo}/commits?per_page=1')
    if d is None: return 0
    m = re.search(r'page=(\d+)>; rel="last"', h.get('Link', '') if h else '')
    return int(m.group(1)) if m else len(d)
def passes(m):
    return (not m['fork'] and not m['archived'] and m['commits'] >= 10 and m['age_days'] >= 14 and not m['template_name'])

def stage_enrich(tool):
    path = f'{D}/repos.json'
    repos = json.load(open(path)) if os.path.exists(path) else {}
    cands = [json.loads(l) for l in open(f'{D}/candidates_{tool}.jsonl')]
    rs = sorted({c['repo'] for c in cands}); random.Random(SEED).shuffle(rs)
    npass = sum(1 for r in rs if r in repos and repos[r].get('pass'))
    for r in rs:
        if npass >= N_PASS: break
        if r in repos: continue
        d, _ = req(f'https://api.github.com/repos/{r}')
        if not d: repos[r] = {'pass': False, 'missing': True}; continue
        created = time.mktime(time.strptime(d['created_at'], '%Y-%m-%dT%H:%M:%SZ'))
        m = {'fork': d['fork'], 'archived': d['archived'], 'stars': d['stargazers_count'], 'language': d['language'],
             'created_at': d['created_at'], 'pushed_at': d['pushed_at'], 'default_branch': d['default_branch'],
             'age_days': int((time.time() - created) / 86400), 'template_name': bool(TEMPLATE_NAME.search(r.split('/')[1])),
             'is_template': d.get('is_template', False), 'size_kb': d['size']}
        m['commits'] = commit_count(r)
        m['pass'] = passes(m) and not m['is_template']
        repos[r] = m; npass += m['pass']
        if len(repos) % 20 == 0: json.dump(repos, open(path, 'w')); log(tool, 'enriched', len(repos), 'pass', npass)
    json.dump(repos, open(path, 'w')); log(tool, 'enrich done, pass', npass)

PLACEHOLDER = re.compile(r'\[FEATURE NAME\]|\[###-feature-name\]|\{project_name\}|\[Phase Name\]')
def get_text(repo, path, ref):
    b, _ = req(f'https://api.github.com/repos/{repo}/contents/{urllib.parse.quote(path)}?ref={ref}', 'application/vnd.github.raw', raw=True)
    return b.decode('utf-8', 'replace') if b else None
def history(repo, path):
    d, _ = req(f'https://api.github.com/repos/{repo}/commits?' + urllib.parse.urlencode({'path': path, 'per_page': 100}))
    return [{'sha': c['sha'], 'date': c['commit']['author']['date'], 'author': (c.get('author') or {}).get('login') or c['commit']['author']['name'],
             'committer': c['commit']['committer']['name'], 'msg': c['commit']['message'][:300]} for c in (d or [])]

def stage_fetch(tool):
    repos = json.load(open(f'{D}/repos.json'))
    cands = [json.loads(l) for l in open(f'{D}/candidates_{tool}.jsonl')]
    by = {}
    for c in cands: by.setdefault(c['repo'], []).append(c['path'])
    od = f'{D}/artifacts/{tool}'; os.makedirs(od, exist_ok=True)
    chosen = [r for r in by if repos.get(r, {}).get('pass')]
    for i, r in enumerate(sorted(chosen)):
        fn = f"{od}/{r.replace('/', '__')}.json"
        if os.path.exists(fn): continue
        ref = repos[r]['default_branch']; rnd = random.Random(f'{SEED}{r}')
        paths = sorted(by[r]); rnd.shuffle(paths)
        unit = None
        for p in paths:                      # first non-placeholder artifact in random order
            t = get_text(r, p, ref)
            if t and not PLACEHOLDER.search(t): unit = (p, t); break
        rec = {'tool': tool, 'repo': r, 'n_candidate_files': len(by[r]), 'files': {}}
        if unit:
            p, t = unit; rec['main'] = p; rec['files'][p] = t; rec['history'] = {p: history(r, p)}
            dirp = p.rsplit('/', 1)[0]
            if TOOLS[tool]['unit'] == 'dir':
                lst, _ = req(f'https://api.github.com/repos/{r}/contents/{urllib.parse.quote(dirp)}?ref={ref}')
                for e in (lst or []):
                    if e['type'] == 'file' and e['name'] != p.rsplit('/', 1)[1] and e['name'].endswith('.md') and e['size'] < 300000:
                        if tool == 'gsd' and not re.search(r'(DISCUSSION-LOG|RESEARCH|CONTEXT)', e['name']): continue
                        tt = get_text(r, e['path'], ref)
                        if tt: rec['files'][e['path']] = tt; rec['history'][e['path']] = history(r, e['path'])
        json.dump(rec, open(fn, 'w'))
        if i % 10 == 0: log(tool, 'fetched', i + 1, '/', len(chosen))
    log(tool, 'fetch done')

if __name__ == '__main__':
    tools = sys.argv[1:] or list(TOOLS)
    for t in tools: stage_search(t)
    for t in tools: stage_enrich(t)
    for t in tools: stage_fetch(t)
    log('ALL DONE')
