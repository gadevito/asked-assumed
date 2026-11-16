import json,re,collections
S=json.load(open('specs.json'))
def sec(t,name):
    m=re.search(r'^#{2,3}\s*'+name+r'[^\n]*$(.*?)(?=^#{1,3} (?!#))',t+'\n## END',re.M|re.S); return m.group(1) if m else None
n=len(S); ass=0; nA=[]; nQ=[]; needs=0
for s in S:
    t=s['text']; a=sec(t,r'Assumptions')
    if a: ass+=1; nA.append(len(re.findall(r'^\s*[-*\d]+[.)]?\s+\S',a,re.M)))
    if 'NEEDS CLARIFICATION' in t: needs+=1
print('files',n,'with Assumptions section',ass, 'median assumption bullets',sorted(nA)[len(nA)//2] if nA else 0,'| still containing [NEEDS CLARIFICATION]',needs)
qa=json.load(open('qa.json'))
impl=re.compile(r'(?i)`|\b(api|endpoint|database|table|column|thread|subprocess|cli|json|yaml|cache|framework|library|class|function|module|schema|ci/cd|docker|env(ironment)? var|config)\b')
print('Q with technical/implementation cues:',sum(1 for x in qa if impl.search(x['q']))/len(qa))
import random; random.seed(3)
for s in random.sample([s for s in S if sec(s['text'],'Assumptions')],3): print('=== ',s['repo'],'\n',sec(s['text'],'Assumptions')[:600])
