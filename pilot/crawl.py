import os, json, time, urllib.request, urllib.parse, sys
TOK=os.environ['GITHUB_TOKEN']
H={'Authorization':f'Bearer {TOK}','Accept':'application/vnd.github.text-match+json','User-Agent':'refsq-pilot'}
def get(url,accept=None):
    h=dict(H); 
    if accept: h['Accept']=accept
    for i in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=h),timeout=30) as r: return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (403,429): time.sleep(30); continue
            raise
q='"## Clarifications" "### Session" "→ A:" filename:spec.md'
items=[]
for p in range(1,int(sys.argv[1])+1):
    d=json.loads(get('https://api.github.com/search/code?'+urllib.parse.urlencode({'q':q,'per_page':100,'page':p})))
    print('page',p,'total',d['total_count'],len(d['items']),file=sys.stderr)
    items+=d['items']; time.sleep(7)
out=[]
seen=set()
for it in items:
    repo=it['repository']['full_name']; path=it['path']
    if (repo,path) in seen: continue
    seen.add((repo,path))
    try: txt=get(it['url'],'application/vnd.github.raw').decode('utf-8','replace')
    except Exception as e: print('ERR',repo,path,e,file=sys.stderr); continue
    out.append({'repo':repo,'path':path,'sha':it['sha'],'text':txt})
json.dump(out,open('specs.json','w'))
print(len(out),'files',len({o['repo'] for o in out}),'repos')
