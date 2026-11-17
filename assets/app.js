(() => {
  'use strict';
  const form = document.querySelector('[data-filters]');
  const container = document.querySelector('[data-entries]');
  if (!form || !container) return;
  const entries = [...container.querySelectorAll('[data-entry]')];
  const fields = [...form.querySelectorAll('.controls input[name],.controls select[name]')];
  const field = name => fields.find(input => input.name === name);
  const sortControl = form.querySelector('[data-sort]');
  const count = document.querySelector('[data-count]');
  const empty = document.querySelector('[data-empty]');
  const status = document.querySelector('[data-filter-status]');
  const viewButtons = [...document.querySelectorAll('button[data-view]')];
  const records = JSON.parse(document.getElementById('catalog-data')?.textContent || '[]');
  const recordMap = new Map(records.map(paper => [paper.id, paper]));
  const entryMap = new Map(entries.map(entry => [entry.id, entry]));
  const searchText = new Map(entries.map(entry => [entry.id, entry.textContent.toLocaleLowerCase()]));
  const relevanceOrder = { direct: 0, enabling: 1, foundation: 2 };
  const titleOrder = new Intl.Collator('en', { sensitivity: 'base', numeric: true });
  let view = 'list';
  let queryTimer;

  function readURL() {
    const params = new URLSearchParams(location.search);
    fields.forEach(input => {
      const value = params.get(input.name) || '';
      input.value = input.tagName === 'SELECT' && ![...input.options].some(option => option.value === value) ? '' : value;
    });
    view = params.get('view') === 'cards' ? 'cards' : 'list';
    const sort = params.get('sort');
    sortControl.value = ['oldest', 'title'].includes(sort) ? sort : 'newest';
  }

  function writeURL(mode = 'push', hash) {
    const url = new URL(location.href);
    fields.forEach(input => input.value ? url.searchParams.set(input.name, input.value) : url.searchParams.delete(input.name));
    view === 'cards' ? url.searchParams.set('view', view) : url.searchParams.delete('view');
    sortControl.value !== 'newest' ? url.searchParams.set('sort', sortControl.value) : url.searchParams.delete('sort');
    if (hash !== undefined) url.hash = hash;
    if (url.href === location.href) return;
    try {
      history[mode === 'replace' ? 'replaceState' : 'pushState'](null, '', url.href);
    } catch (_) {
      // Some file:// browsers restrict History API writes; all local controls still work.
    }
  }

  function render() {
    const values = Object.fromEntries(fields.map(input => [input.name, input.value]));
    const terms = (values.q || '').trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    const ordered = [...entries].sort((a, b) => {
      const byTitle = titleOrder.compare(a.dataset.title, b.dataset.title);
      if (sortControl.value === 'title') return byTitle;
      const byYear = Number(a.dataset.year) - Number(b.dataset.year);
      return (sortControl.value === 'oldest' ? byYear : -byYear) ||
        relevanceOrder[a.dataset.relevance] - relevanceOrder[b.dataset.relevance] || byTitle;
    });
    let visible = 0;
    ordered.forEach(entry => {
      const matches = terms.every(term => searchText.get(entry.id).includes(term)) && fields.every(input => {
        if (input.name === 'q' || !input.value) return true;
        if (input.name === 'year' && ['recent', 'background'].includes(input.value)) return entry.dataset.period === input.value;
        return entry.dataset[input.name] === input.value;
      });
      entry.hidden = !matches;
      if (matches) visible++;
      container.append(entry);
    });
    container.dataset.view = view;
    viewButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.view === view)));
    document.querySelectorAll('[data-quick-year]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.quickYear === values.year)));
    document.querySelector('[data-quick-code]')?.setAttribute('aria-pressed', String(values.code === 'yes'));
    count.textContent = `显示 ${visible} / ${entries.length} 条`;
    empty.hidden = visible > 0;
    const labels = fields.filter(input => input.value).map(input => input.name === 'q' ? `关键词：${input.value}` : input.selectedOptions[0].textContent);
    const sortLabel = { newest: '年份新到旧', oldest: '年份旧到新', title: '标题 A–Z' }[sortControl.value];
    status.textContent = `${labels.length ? labels.join(' · ') : '全部论文'} · ${sortLabel} · ${view === 'list' ? '紧凑列表' : '详细卡片'}`;
  }

  function hashID() {
    try { return decodeURIComponent(location.hash.slice(1)); } catch (_) { return ''; }
  }

  function commit(clearPaperHash = true) {
    clearTimeout(queryTimer);
    render();
    writeURL('push', clearPaperHash && entryMap.has(hashID()) ? 'catalog' : undefined);
  }

  function revealTarget(id, scroll = true) {
    const target = document.getElementById(id);
    if (!target) return;
    const entry = entryMap.get(id);
    if (entry) {
      if (entry.hidden) {
        fields.forEach(input => { input.value = ''; });
        render();
        writeURL('replace');
      }
      const details = entry.querySelector('details');
      if (details) details.open = true;
      entry.dataset.expanded = 'true';
    }
    for (let parent = target.parentElement; parent; parent = parent.parentElement) {
      if (parent.tagName === 'DETAILS') parent.open = true;
    }
    if (scroll) requestAnimationFrame(() => target.scrollIntoView({ block: 'start' }));
  }

  fields.forEach(input => {
    if (input.tagName === 'INPUT') {
      input.addEventListener('input', () => {
        render();
        clearTimeout(queryTimer);
        queryTimer = setTimeout(() => commit(), 350);
      });
      input.addEventListener('change', () => commit());
    } else input.addEventListener('change', () => commit());
  });
  form.addEventListener('submit', event => { event.preventDefault(); commit(); });
  sortControl.addEventListener('change', () => commit(false));
  viewButtons.forEach(button => button.addEventListener('click', () => { view = button.dataset.view; commit(false); }));
  document.querySelectorAll('[data-reset]').forEach(button => button.addEventListener('click', () => {
    fields.forEach(input => { input.value = ''; });
    commit();
  }));
  document.querySelectorAll('[data-quick-year]').forEach(button => button.addEventListener('click', () => {
    const input = field('year');
    input.value = input.value === button.dataset.quickYear ? '' : button.dataset.quickYear;
    commit();
  }));
  document.querySelector('[data-quick-code]')?.addEventListener('click', () => {
    field('code').value = field('code').value === 'yes' ? '' : 'yes';
    commit();
  });
  document.querySelector('[data-expand]')?.addEventListener('click', () => {
    entries.filter(entry => !entry.hidden).forEach(entry => { entry.querySelector('details').open = true; entry.dataset.expanded = 'true'; });
  });
  document.querySelector('[data-collapse]')?.addEventListener('click', () => {
    entries.forEach(entry => { entry.querySelector('details').open = false; entry.dataset.expanded = 'false'; });
  });
  entries.forEach(entry => entry.querySelector('details')?.addEventListener('toggle', event => {
    entry.dataset.expanded = String(event.currentTarget.open);
  }));
  document.querySelectorAll('[data-filter-category]').forEach(anchor => anchor.addEventListener('click', event => {
    event.preventDefault();
    fields.forEach(input => { input.value = ''; });
    field('category').value = anchor.dataset.filterCategory;
    clearTimeout(queryTimer);
    render();
    writeURL('push', 'catalog');
    document.getElementById('catalog').scrollIntoView();
  }));
  document.querySelectorAll('a[href^="#"]:not([data-filter-category])').forEach(anchor => anchor.addEventListener('click', event => {
    let id;
    try { id = decodeURIComponent(anchor.getAttribute('href').slice(1)); } catch (_) { return; }
    const target = document.getElementById(id);
    if (!target) return;
    event.preventDefault();
    clearTimeout(queryTimer);
    if (entryMap.get(id)?.hidden) {
      fields.forEach(input => { input.value = ''; });
      render();
    }
    writeURL('push', id);
    revealTarget(id);
  }));
  window.addEventListener('popstate', () => {
    clearTimeout(queryTimer);
    readURL();
    render();
    if (location.hash) revealTarget(hashID());
  });
  window.addEventListener('hashchange', () => {
    if (location.hash) revealTarget(hashID());
  });

  function download(content, name, type) {
    const url = URL.createObjectURL(new Blob([content], { type }));
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = name;
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  document.querySelector('[data-export]')?.addEventListener('click', () => {
    const visible = [...container.querySelectorAll('[data-entry]')].filter(entry => !entry.hidden).map(entry => recordMap.get(entry.id));
    download(JSON.stringify(visible, null, 2), 'rsi-papers.json', 'application/json');
  });
  const bib = paper => `@inproceedings{${paper.id},\n  title = {${paper.title.replace(/[{}]/g, '')}},\n  author = {${(paper.bib_authors || paper.authors).replace(/[{}]/g, '')}},\n  booktitle = {${paper.venue}},\n  year = {${paper.year}},\n  url = {${paper.url}}\n}`;
  document.querySelectorAll('[data-cite]').forEach(button => button.addEventListener('click', () => {
    const paper = recordMap.get(button.dataset.cite);
    if (!paper) return;
    if (paper.bib_authors) download(bib(paper), `${paper.id}.bib`, 'application/x-bibtex');
    else download(`${paper.authors}. ${paper.title}. ${paper.venue}, ${paper.year}.\n${paper.url}\n\n作者为网页题录中的简写；完整引用请以论文官方记录为准。`, `${paper.id}.txt`, 'text/plain;charset=utf-8');
  }));
  readURL();
  render();
  if (location.hash) revealTarget(hashID());
})();
