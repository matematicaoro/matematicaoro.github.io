#!/usr/bin/env python3
"""Registra la data del primo commit che ha aggiunto ogni immagine al repository.
Non modifica le date già registrate, anche se un'immagine viene sostituita.
"""
import json, pathlib, subprocess
p=pathlib.Path('fumetti/chiara-luca/tavole.json')
items=json.loads(p.read_text(encoding='utf-8'))
changed=False
for item in items:
    if item.get('published_at') or not item.get('pages'):
        continue
    dates=[]
    for relative in item['pages']:
        file='fumetti/chiara-luca/'+relative
        if not pathlib.Path(file).is_file():
            continue
        proc=subprocess.run(['git','log','--diff-filter=A','--format=%cI','--',file],capture_output=True,text=True,check=True)
        found=[line.strip() for line in proc.stdout.splitlines() if line.strip()]
        if found: dates.append(min(found))
    if dates:
        item['published_at']=min(dates)[:10]
        changed=True
if changed:
    p.write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Date registrate nel catalogo')
else:
    print('Nessuna nuova data da registrare')
