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
    from html import unescape
    s=path.read_text(encoding='utf-8',errors='replace')[:120000]
    def clean(value):
        value=re.sub(r'<[^>]*>', ' ', value)
        value=unescape(re.sub(r'\s+', ' ', value)).strip()
        value=re.sub(r'^(?:Matematica\s*Oro)\s*(?:[-–—|·:]\s*)?', '', value, flags=re.I)
        value=re.sub(r'\s*(?:[-–—|·:]\s*)(?:Matematica\s*Oro)$', '', value, flags=re.I)
        return value.strip(' -–—|·:')
    # Prefer the visible page heading: many exercise <title> tags are file codes.
    for pattern in (r'<h1\b[^>]*>(.*?)</h1\s*>', r'<h2\b[^>]*>(.*?)</h2\s*>', r'<title\b[^>]*>(.*?)</title\s*>'):
        for m in re.finditer(pattern,s,re.I|re.S):
            title=clean(m.group(1))
            if title and not re.fullmatch(r'(?:Matematica\s*Oro|Esercizi|Lezioni|Schemi|Teoria)',title,re.I):
                # Reject generic HTML headings and short technical codes.
                if not re.fullmatch(r'(?:ese[_ -]?)?(?:scomp|diseq|eq|fraz)[_\s-]*[0-9ivx_-]*',title,re.I):
                    return title[:110]
    # Fallback: expand common abbreviations rather than displaying file codes.
    slug=path.parent.name if path.name.lower()=='index.html' else path.stem
    slug=re.sub(r'^(?:ese|esercizi)[_-]+','',slug,flags=re.I)
    words={'scomp':'Scomposizione di polinomi','diseq':'Disequazioni','eq':'Equazioni','fraz':'Frazioni','mcd':'MCD','mcm':'mcm','polinomi':'polinomi','algebriche':'algebriche','grado':'grado','fratte':'fratte','ripasso':'ripasso'}
    tokens=re.split(r'[_\s-]+',slug)
    result=' '.join(words.get(t.lower(),t) for t in tokens)
    return result.strip().capitalize()[:110] or 'Scheda di esercizi'

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
