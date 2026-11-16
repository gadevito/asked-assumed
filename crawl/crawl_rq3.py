"""RQ3 dataset: GSD discussion logs (option tables with recommended/selected marks).
Same quality filters as crawl.py; max 5 logs per repo (random, seeded) to limit clustering."""
import json, os, random, time, urllib.parse, urllib.request
import crawl as C
C.TOOLS['gsdlog'] = {'q': "\"User's choice\" \"| Option\" path:.planning filename:DISCUSSION-LOG.md", 'unit': 'file'}
C.N_PASS = 10**9          # enrich all candidate repos
MAX_PER_REPO = 5
def raw(repo, branch, path):
    u = f'https://raw.githubusercontent.com/{repo}/{urllib.parse.quote(branch)}/{urllib.parse.quote(path)}'
    for i in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'refsq'}), timeout=30).read().decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            if e.code == 404: return None
            time.sleep(5)
        except Exception: time.sleep(5)
if __name__ == '__main__':
    C.stage_search('gsdlog')
    C.stage_enrich('gsdlog')
    repos = json.load(open(f'{C.D}/repos.json'))
    cands = [json.loads(l) for l in open(f'{C.D}/candidates_gsdlog.jsonl')]
    by = {}
    for c in cands: by.setdefault(c['repo'], []).append(c['path'])
    out = f'{C.D}/gsdlogs.jsonl'; done = set()
    if os.path.exists(out): done = {json.loads(l)['repo'] for l in open(out)}
    with open(out, 'a') as f:
        for r in sorted(by):
            if r in done or not repos.get(r, {}).get('pass'): continue
            ps = sorted(by[r]); random.Random(f'{C.SEED}{r}').shuffle(ps)
            for p in ps[:MAX_PER_REPO]:
                t = raw(r, repos[r]['default_branch'], p)
                if t: f.write(json.dumps({'repo': r, 'path': p, 'text': t}) + '\n')
            f.flush()
    C.log('RQ3 DONE')
