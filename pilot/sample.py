import os,json,time,urllib.request,urllib.parse,sys,re
TOK=os.environ['GITHUB_TOKEN']
def get(u,acc='application/vnd.github+json'):
    return urllib.request.urlopen(urllib.request.Request(u,headers={'Authorization':f'Bearer {TOK}','User-Agent':'p','Accept':acc}),timeout=30).read()
def fetch(q,n,out):
    d=json.loads(get('https://api.github.com/search/code?'+urllib.parse.urlencode({'q':q,'per_page':n})))
    res=[]
    for it in d['items']:
        try: res.append({'repo':it['repository']['full_name'],'path':it['path'],'text':get(it['url'],'application/vnd.github.raw').decode('utf-8','replace')})
        except Exception as e: pass
    json.dump(res,open(out,'w')); return res
g=fetch("\"User's choice\" path:.planning",100,'gsd_logs.json'); time.sleep(7)
b=fetch('"## 8. Open Questions" "Assumptions Index"',50,'bmad_prd.json')
print(len(g),len(b))
