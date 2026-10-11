#!/usr/bin/env python3
"""Crea il catalogo novità da prime aggiunte Git delle pagine delle sezioni.
Non considera modifiche successive come nuove pubblicazioni.
"""
import json,subprocess,pathlib,re,datetime
ROOT=pathlib.Path('.')
OUT=ROOT/'novita-sezioni.json'
old=json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else {}
sections=('lezioni','esercizi','teoria','schemi')
def first_date(path):
    r=subprocess.run(['git','log','--follow','--diff-filter=A','--format=%aI','--',path],capture_output=True,text=True,check=True)
    dates=[x.strip()[:10] for x in r.stdout.splitlines() if x.strip()]
    return min(dates) if dates else None
def title_of(path):
    s=path.read_text(encoding='utf-8',errors='replace')[:40000]
    m=re.search(r'<title[^>]*>(.*?)</title>',s,re.I|re.S)
    if not m:return path.parent.name.replace('_',' ').replace('-',' ').capitalize()
    return re.sub(r'\s+',' ',re.sub('<[^>]+>','',m.group(1))).strip()[:110]
result={}
for sec in sections:
    previous={x['url']:x for x in old.get(sec,[]) if 'url' in x}
    rows=[]
    folder=ROOT/sec
    if folder.exists():
        for f in sorted(folder.rglob('index.html')):
            if f==folder/'index.html':continue
            rel=f.as_posix()
            url=rel
            date=previous.get(url,{}).get('published_at') or first_date(rel)
            if not date:continue
            rows.append({'title':title_of(f),'url':url,'published_at':date})
        # Include single HTML lesson files directly in the section folder.
        for f in sorted(folder.glob('*.html')):
            if f.name=='index.html':continue
            rel=f.as_posix();date=previous.get(rel,{}).get('published_at') or first_date(rel)
            if date:rows.append({'title':title_of(f),'url':rel,'published_at':date})
    rows.sort(key=lambda x:(x['published_at'],x['url']),reverse=True)
    result[sec]=rows
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Catalogo aggiornato:',', '.join(f'{k}={len(v)}' for k,v in result.items()))
