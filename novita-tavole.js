/* MatematicaOro: novità ordinate per data di prima pubblicazione */
(function(){
  const target=document.querySelector('[data-mo-latest-comics]');
  if(!target)return;
  const catalog=target.getAttribute('data-catalog');
  const viewer=target.getAttribute('data-viewer');
  fetch(catalog+'?v='+Math.floor(Date.now()/300000),{cache:'no-store'})
    .then(r=>{if(!r.ok)throw new Error('Catalogo non disponibile');return r.json()})
    .then(items=>{
      const dated=items.filter(x=>x.published_at && /^\d{4}-\d{2}-\d{2}/.test(x.published_at));
      if(!dated.length)return; // conserva i link statici finché le date non sono state registrate
      dated.sort((a,b)=>b.published_at.localeCompare(a.published_at)||b.id.localeCompare(a.id));
      target.replaceChildren();
      dated.slice(0,3).forEach(x=>{
        const a=document.createElement('a');
        a.href=viewer+'#'+encodeURIComponent(x.id);
        a.textContent=x.id+' · '+x.title+' →';
        a.title='Pubblicata il '+new Date(x.published_at.slice(0,10)+'T12:00:00').toLocaleDateString('it-IT');
        if(target.classList.contains('hero-actions'))a.className='btn btn-light';
        target.appendChild(a);
      });
    }).catch(()=>{});
})();
