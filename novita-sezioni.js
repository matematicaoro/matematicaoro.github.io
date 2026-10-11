/* Aggiornamento automatico delle novità delle sezioni dal catalogo generato su GitHub. */
(()=>{const boxes=[...document.querySelectorAll('[data-mo-section]')];if(!boxes.length)return;
fetch('novita-sezioni.json?v='+Math.floor(Date.now()/300000),{cache:'no-store'})
.then(r=>{if(!r.ok)throw Error('Catalogo assente');return r.json()})
.then(data=>boxes.forEach(box=>{const rows=(data[box.dataset.moSection]||[]).slice(0,3);box.replaceChildren();
if(!rows.length){const s=document.createElement('span');s.className='news-empty';s.textContent='Nessuna novità pubblicata.';box.append(s);return;}
rows.forEach(x=>{const a=document.createElement('a');a.href=x.url;a.textContent=x.title+' →';a.title='Pubblicato il '+x.published_at;box.append(a);});
})).catch(()=>{});
})();
