(() => {
  'use strict';
  const entries = [...document.querySelectorAll('[data-entry]')];
  const form = document.querySelector('[data-filters]');
  const count = document.querySelector('[data-count]');
  const empty = document.querySelector('[data-empty]');
  const params = new URLSearchParams(location.search);
  const fields = form ? [...form.querySelectorAll('input[name],select[name]')] : [];
  const dataNode = document.getElementById('catalog-data');
  const records = dataNode ? JSON.parse(dataNode.textContent) : [];
  const recordMap = new Map(records.map(p => [p.id,p]));
  function apply(updateURL=true) {
    const filters = Object.fromEntries(fields.map(f => [f.name,f.value]));
    const terms = (filters.q || '').trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let visible = 0;
    entries.forEach(e => {
      const match = terms.every(t => e.textContent.toLocaleLowerCase().includes(t)) &&
        fields.every(f => f.name === 'q' || !f.value ||
          (f.name === 'year' && ['recent','background'].includes(f.value)
            ? e.dataset.period === f.value
            : f.name === 'code' ? e.dataset.code === 'yes' : e.dataset[f.name] === f.value));
      e.hidden = !match;
      if (match) visible++;
    });
    if(count) count.textContent = `显示 ${visible} / ${entries.length} 条`;
    if(empty) empty.hidden = visible > 0;
    if(updateURL && form){
      const url = new URL(location.href);
      fields.forEach(f => f.value ? url.searchParams.set(f.name,f.value) : url.searchParams.delete(f.name));
      try { history.replaceState(null,'',url); } catch (_) { /* file:// remains fully usable */ }
    }
  }
  fields.forEach(f => { if(params.has(f.name)) f.value=params.get(f.name); f.addEventListener(f.tagName==='INPUT'?'input':'change',()=>apply()); });
  form?.addEventListener('submit',e=>e.preventDefault());
  document.querySelector('[data-reset]')?.addEventListener('click',()=>{fields.forEach(f=>f.value='');apply();});
  document.querySelector('[data-expand]')?.addEventListener('click',()=>entries.filter(e=>!e.hidden).forEach(e=>e.querySelectorAll('details').forEach(d=>d.open=true)));
  document.querySelector('[data-collapse]')?.addEventListener('click',()=>entries.forEach(e=>e.querySelectorAll('details').forEach(d=>d.open=false)));
  document.querySelectorAll('[data-filter-category]').forEach(a=>a.addEventListener('click',e=>{
    const f=fields.find(f=>f.name==='category'); if(!f)return; e.preventDefault(); fields.forEach(x=>x.value=''); f.value=a.dataset.filterCategory;apply();document.getElementById('catalog')?.scrollIntoView();
  }));
  function download(content,name,type){const url=URL.createObjectURL(new Blob([content],{type}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  document.querySelector('[data-export]')?.addEventListener('click',()=>{const visible=new Set(entries.filter(e=>!e.hidden).map(e=>e.id));download(JSON.stringify(records.filter(p=>visible.has(p.id)),null,2),'rsi-papers.json','application/json');});
  const bib = p => `@inproceedings{${p.id},\n  title = {${p.title.replace(/[{}]/g,'')}},\n  author = {${(p.bib_authors || p.authors).replace(/[{}]/g,'')}},\n  booktitle = {${p.venue}},\n  year = {${p.year}},\n  url = {${p.url}}\n}`;
  document.querySelectorAll('[data-cite]').forEach(b=>b.addEventListener('click',()=>{const p=recordMap.get(b.dataset.cite);if(!p)return;if(p.bib_authors){download(bib(p),`${p.id}.bib`,'application/x-bibtex');}else{download(`${p.authors}. ${p.title}. ${p.venue}, ${p.year}.\n${p.url}\n\n作者为网页题录中的简写；完整引用请以论文官方记录为准。`,`${p.id}.txt`,'text/plain;charset=utf-8');}}));
  document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',()=>{const id=decodeURIComponent(a.getAttribute('href').slice(1));const entry=document.getElementById(id);if(entry?.hasAttribute('data-entry') && entry.hidden){fields.forEach(f=>f.value='');apply();}}));
  apply(false);
  if(location.hash){const target=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(target?.hasAttribute('data-entry')&&target.hidden){fields.forEach(f=>f.value='');apply();}requestAnimationFrame(()=>target?.scrollIntoView());}
})();
