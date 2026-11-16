import json,re,collections,random
S=json.load(open('specs.json'))
qa=[]
for s in S:
    t=s['text']; m=re.search(r'^## Clarifications\s*$(.*?)(?=^## (?!#))',t+'\n## END',re.M|re.S)
    if not m: continue
    sess=None
    for line in m.group(1).splitlines():
        h=re.match(r'^###\s+Session\s+(\S+)',line)
        if h: sess=h.group(1); continue
        q=re.match(r'^\s*[-*]\s*Q:\s*(.*?)\s*→\s*A:\s*(.*)$',line)
        if q: qa.append({'repo':s['repo'],'path':s['path'],'session':sess,'q':q.group(1),'a':q.group(2)})
json.dump(qa,open('qa.json','w'),ensure_ascii=False,indent=0)
print('QA',len(qa),'files with QA',len({(x['repo'],x['path']) for x in qa}))
per=collections.Counter((x['repo'],x['path']) for x in qa); print('QA per file: median',sorted(per.values())[len(per)//2],'max',max(per.values()))
print('sessions/file', collections.Counter(len({x['session'] for x in qa if (x['repo'],x['path'])==k}) for k in per).most_common(5))
A=[x['a'] for x in qa]
pat={'option letter':r'^\s*\(?(Option\s+)?[A-E]\)?\b[\s:.\-–—)]','mentions recommended':r'(?i)recommend','"Option X"':r'(?i)\boption\s+[A-E]\b','short (<=5 words)':None}
for k,p in pat.items():
    n=sum(1 for a in A if (len(a.split())<=5 if p is None else re.search(p,a)))
    print(f'{k}: {n} ({n/len(A):.0%})')
print('answer len words median',sorted(len(a.split()) for a in A)[len(A)//2])
random.seed(1)
for x in random.sample(qa,25): print('---\nQ:',x['q'][:200],'\nA:',x['a'][:200])
