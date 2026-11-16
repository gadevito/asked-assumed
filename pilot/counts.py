import os,json,time,urllib.request,urllib.parse
TOK=os.environ['GITHUB_TOKEN']
def c(q):
    r=urllib.request.Request('https://api.github.com/search/code?'+urllib.parse.urlencode({'q':q,'per_page':1}),headers={'Authorization':f'Bearer {TOK}','User-Agent':'p'})
    try: return json.load(urllib.request.urlopen(r))['total_count']
    except Exception as e: return str(e)
Q={
 'SpecKit clarifications':'"## Clarifications" "### Session" filename:spec.md',
 'SpecKit assumptions':'"## Assumptions" path:specs filename:spec.md',
 'GSD discussion-log':"\"User's choice\" path:.planning",
 'GSD CONTEXT discretion':"\"Claude's Discretion\" path:.planning",
 'GSD assumptions log':'"## Assumptions Log" path:.planning',
 'GSD auto mode':'"[auto]" "recommended" path:.planning',
 'BMAD assumptions index':'"Assumptions Index" "[ASSUMPTION"',
 'BMAD memlog':'"(assumption)" filename:.memlog.md',
 'BMAD open questions prd':'"## 8. Open Questions"',
 'BMAD any _bmad-output':'path:_bmad-output prd',
 'OpenSpec design':'"## Decisions" path:openspec/changes filename:design.md',
 'OpenSpec open questions':'"Open Questions" path:openspec/changes filename:design.md',
 'Kiro requirements':'path:.kiro/specs filename:requirements.md',
}
for k,q in Q.items(): print(f'{k:28s} {c(q)}'); time.sleep(7)
