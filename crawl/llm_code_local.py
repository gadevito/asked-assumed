"""LLM pre-coding with an open-weight model served by vLLM (OpenAI-compatible endpoint).
Frozen codebook prompt and JSON schema from coding_prompt.py; temperature 0; weights pinned by snapshot hash.

Usage:
  python3 llm_code_local.py pilot|pilot2  [--url http://localhost:8000] [--model openai/gpt-oss-120b] [--effort medium]
  python3 llm_code_local.py all    [...same flags]
Outputs: data/llm_<mode>_<model-tag>.jsonl (resumable).
"""
import argparse, json, os, re, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from coding_prompt import SYSTEM, SCHEMA, user_msg, load, items_all
JSON_INSTR = ('\n\nThink through the tests before answering. Then output only one JSON object with keys '
              '"evidence", "mood", "locus", "concern", "subcode", using exactly the allowed values: '
              + '; '.join(f"{k}: {'|'.join(v['enum'])}" for k, v in SCHEMA['properties'].items() if 'enum' in v) + '.')

ap = argparse.ArgumentParser()
ap.add_argument('mode', choices=['pilot', 'pilot2', 'all'])
ap.add_argument('--url', default='http://localhost:8000')
ap.add_argument('--model', default='openai/gpt-oss-120b')
ap.add_argument('--effort', default='medium', choices=['low', 'medium', 'high', 'xhigh'])
ap.add_argument('--workers', type=int, default=32)
ap.add_argument('--timeout', type=int, default=1200)
ap.add_argument('--fallback-effort', default='medium', help='effort used for one retry after a timeout or invalid output')
ap.add_argument('--free', action='store_true', help='no constrained decoding: model reasons, then emits JSON (validated client-side)')
a = ap.parse_args()
KEY = os.environ['VLLM_API_KEY']

def request(d, effort):
    body = {'model': a.model, 'temperature': 0, 'max_tokens': 8000, 'reasoning_effort': effort,
            'messages': [{'role': 'system', 'content': SYSTEM}, {'role': 'user', 'content': user_msg(d)}]}
    if a.free:
        body['messages'][0]['content'] = SYSTEM + JSON_INSTR
    else:
        body['response_format'] = {'type': 'json_schema', 'json_schema': {'name': 'decision_code', 'schema': SCHEMA, 'strict': True}}
    req = urllib.request.Request(a.url + '/v1/chat/completions', data=json.dumps(body).encode(),
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + KEY})
    r = json.load(urllib.request.urlopen(req, timeout=a.timeout))
    c = r['choices'][0]
    m = re.search(r'\{.*\}', c['message']['content'] or '', re.S)
    out = json.loads(m.group(0))
    bad = [k for k in SCHEMA['required'] if k not in out or ('enum' in SCHEMA['properties'][k] and out[k] not in SCHEMA['properties'][k]['enum'])]
    if bad: raise ValueError(f'invalid fields {bad}')
    return {**out, 'finish': c['finish_reason'], 'usage': r.get('usage'), 'effort_used': effort}

def code(d):
    err = None
    for effort in (a.effort, a.fallback_effort):   # one attempt at the main effort, one fallback
        try: return request(d, effort)
        except Exception as e: err = f'{effort}: {e}'
    return {'error': err}

if __name__ == '__main__':
    if a.mode.startswith('pilot'):
        key = json.load(open('../annotation/pilot_key.json' if a.mode == 'pilot' else '../annotation/pilot_key_round2.json')); D = {d['id']: d for d in load('data/decisions.jsonl')}
        items = [dict(D[k['id']], pid=k['pid']) for k in key]
    else:
        items = items_all()
    tag = a.model.split('/')[-1] + '-' + a.effort + ('-free' if a.free else '')
    out = f'data/llm_{a.mode}_{tag}.jsonl'
    prev = [json.loads(l) for l in open(out)] if os.path.exists(out) else []
    done = {d['id'] for d in prev if 'error' not in d}
    if len(done) < len(prev):  # drop failed rows so they are retried
        with open(out, 'w') as f:
            for d in prev:
                if 'error' not in d: f.write(json.dumps(d, ensure_ascii=False) + '\n')
    todo = [d for d in items if d['id'] not in done]
    print(len(todo), 'to code ->', out)
    with open(out, 'a') as f, ThreadPoolExecutor(a.workers) as ex:
        futs = {ex.submit(code, d): d for d in todo}
        for fu in as_completed(futs):   # write each result as soon as it is ready
            d, res = futs[fu], fu.result()
            f.write(json.dumps({'id': d['id'], 'pid': d.get('pid'), 'model': a.model, 'effort': a.effort, **res}, ensure_ascii=False) + '\n'); f.flush()
    print('done')
