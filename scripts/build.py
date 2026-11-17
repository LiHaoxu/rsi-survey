#!/usr/bin/env python3
"""Build the self-evolving recommendation literature atlas; Python standard library only."""
import json
import re
from pathlib import Path
from html import escape as esc
from collections import Counter
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / 'config.json').read_text())
BENCH_PROTOCOL_URL = CFG['bench_url'].rsplit('/', 1)[0] + '/protocols.html'
CATEGORIES = {
    'self-evolution': ('自主改进与自纠正', '利用误差、反思与验证信号，决定下一轮如何改进。'),
    'agents': ('智能体与反馈记忆', '把交互经验写入记忆、提示或规划，改善后续推荐。'),
    'synthetic': ('合成监督与自训练', '利用伪标签、生成样本、蒸馏或自监督信号更新模型。'),
    'continual': ('持续学习与适应', '追踪兴趣与环境变化，协调新知识和历史能力。'),
    'reinforcement': ('探索与策略学习', '从交互回报中学习策略，关注长期效用和探索代价。'),
    'foundations': ('经典骨干与评测基础', '为闭环方法提供推荐骨干、偏差校正与可信评估。'),
}
RELEVANCE = {'direct': '直接闭环', 'enabling': '支撑方法', 'foundation': '经典基础'}
TYPES = {'full': 'Research paper', 'short': 'Short paper', 'perspective': 'Perspective', 'industry': 'Industry paper', 'demo': 'Demo'}

def e(s): return esc(str(s), quote=True)
def link(url, label, cls=''):
    return f'<a class="{cls}" href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(label)} ↗</a>'
def options(values, all_label):
    return '<option value="">' + e(all_label) + '</option>' + ''.join(f'<option value="{e(k)}">{e(v)}</option>' for k,v in values)

papers = []
for name in ['recent.json', 'classics.json']:
    path = ROOT / 'data' / name
    if not path.exists():
        raise SystemExit(f'Missing research source: {path}')
    papers.extend(json.loads(path.read_text()))
ids = set()
for p in papers:
    for key in ['id','title','short','year','venue','category','relevance','authors','problem','method','loop','evidence','limitation','url','code','sources','tags','influence_reason','verified']:
        if key not in p: raise ValueError(f'{p.get("id")}: missing {key}')
    if p['id'] in ids or not re.fullmatch('[a-z0-9-]+',p['id']): raise ValueError(f'Invalid/duplicate ID {p["id"]}')
    ids.add(p['id'])
    if p['category'] not in CATEGORIES or p['relevance'] not in RELEVANCE: raise ValueError(f'Unknown taxonomy: {p["id"]}')
    if not isinstance(p['year'],int) or not 1990 <= p['year'] <= 2026: raise ValueError('Invalid year')
    for u in [p['url'],*p['sources'],*([p['code']] if p['code'] else [])]:
        if urlparse(u).scheme != 'https' or not urlparse(u).netloc: raise ValueError(f'Invalid URL {u}')
papers.sort(key=lambda p:(-p['year'], {'direct':0,'enabling':1,'foundation':2}[p['relevance']],p['title']))
counts = Counter(p['category'] for p in papers)
venues = sorted(set(p['venue'] for p in papers))
by_id = {p['id']:p for p in papers}

def paper_html(p):
    typ = p.get('publication_type','full')
    details = ''.join(f'<p><span class="field-label">{label}</span>{e(p[field])}</p>' for label,field in [('核心方法','method'),('反馈与改进环节','loop'),('论文证据','evidence'),('收录理由 · 编辑判断','influence_reason')])
    sources = ''.join(link(u,f'来源 {i+1}') for i,u in enumerate(p['sources']))
    code = link(p['code'],'官方代码') if p['code'] else '<span class="note">官方代码未核实</span>'
    return f'''<article class="entry" id="{e(p['id'])}" data-entry data-year="{p['year']}" data-venue="{e(p['venue'])}" data-category="{e(p['category'])}" data-relevance="{e(p['relevance'])}" data-code="{'yes' if p['code'] else 'no'}">
<div class="entry-top"><span class="badge venue">{e(p['venue'])} {p['year']}</span><span class="badge {p['relevance']}">{RELEVANCE[p['relevance']]}</span><span>{e(CATEGORIES[p['category']][0])}</span><span>·</span><span>{e(TYPES.get(typ,typ))}</span></div>
<h3>{link(p['url'],p['title'])}</h3><p class="authors">{e(p['authors'])} · {e(p['short'])}</p>
<p class="summary"><span class="field-label">研究问题</span>{e(p['problem'])}</p>
<div class="tags">{''.join(f'<span class="tag">{e(t)}</span>' for t in p['tags'])}</div>
<details><summary>方法、反馈环节与收录依据</summary><div class="details-grid">{details}</div><p class="limitation"><b>证据边界</b>　{e(p['limitation'])}</p><p class="source-note">来源核对：{e(p['verified'])}。文献核对不等于独立复现。</p><div class="sources">{sources}</div></details>
<div class="sources">{link(p['url'],'论文')}{code}<button type="button" data-cite="{e(p['id'])}">下载引文</button><a href="#{e(p['id'])}" aria-label="{e(p['short'])} 的永久链接"># 永久链接</a></div></article>'''

def references(names):
    refs = [next((p for p in papers if p['id']==n or p['short'].lower()==n.lower()),None) for n in names]
    return ' → '.join(f'<a href="#{e(p["id"])}">{e(p["short"])}</a>' for p in refs if p)

nav = ''.join(f'<a href="#catalog" data-filter-category="{k}">{e(v[0])}<small>{counts[k]:02}</small></a>' for k,v in CATEGORIES.items())
tax = ''.join(f'<a class="taxon" href="#catalog" data-filter-category="{k}"><span class="number">0{i+1}</span><h3>{e(v[0])}</h3><p>{e(v[1])}</p><span class="count">{counts[k]} 篇相关工作 →</span></a>' for i,(k,v) in enumerate(CATEGORIES.items()))
payload = json.dumps(papers,ensure_ascii=False).replace('<','\\u003c')
html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="推荐系统自进化领域顶会文献精选：自主改进、智能体反馈、合成监督、持续学习与强化学习。连接经典基础和2023—2026年代表工作。"><meta name="theme-color" content="#172e2a"><title>RSI Survey · 推荐系统自进化研究图谱</title><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/styles.css"><script src="assets/app.js" defer></script></head>
<body id="top"><a class="skip" href="#main">跳到正文</a><div class="layout"><aside class="sidebar" aria-label="研究目录"><a class="brand" href="index.html">RSI Atlas<span class="mark">SELF-EVOLVING RECOMMENDATION</span></a><div class="switch"><a class="active" href="index.html" aria-current="page">Survey</a><a href="{e(CFG['bench_url'])}">Bench ↗</a></div><nav><div class="nav-label">EXPLORE</div><a href="#taxonomy">研究路线 <small>01</small></a><a href="#catalog">文献目录 <small>02</small></a><a href="#reading">阅读路线 <small>03</small></a><a href="#questions">研究问题 <small>04</small></a><a href="#scope">收录标准 <small>05</small></a></nav><nav><div class="nav-label">RESEARCH TRACKS</div>{nav}</nav><div class="bottom"><span>领域顶会 · 经典与近期代表作</span><span>资料核对 {e(CFG['asof'])}</span><br>{link(CFG['repo_url'],'GitHub / 参与维护')}</div></aside>
<main class="main" id="main"><div class="topline"><span class="mobile-brand">RSI Atlas</span><span class="edition">RESEARCH ATLAS / VOL. 01</span><nav><a href="index.html" aria-current="page">Survey</a><a href="{e(CFG['bench_url'])}">Benchmark ↗</a>{link(CFG['repo_url'],'GitHub')}</nav></div>
<header class="hero"><div class="eyebrow">LITERATURE SURVEY · FOUNDATIONS TO FRONTIERS</div><h1>推荐系统的<br><em>自进化研究图谱</em></h1><p class="lead">从交互中学习，从反馈中改进。梳理推荐系统如何更新数据、模型、策略与记忆，连接经典方法与近年的自进化研究。</p><div class="hero-actions"><a class="btn primary" href="#catalog">浏览文献目录 ↓</a><a class="btn" href="{e(CFG['bench_url'])}">进入评测与复现 ↗</a><span class="status">精选文献 · 持续维护</span></div></header>
<div class="stats"><div class="stat"><strong>{len(papers):02}</strong><span>精选论文</span></div><div class="stat"><strong>{sum(p['year']>=2023 for p in papers):02}</strong><span>2023—2026 近期工作</span></div><div class="stat"><strong>{len(venues):02}</strong><span>领域会议</span></div><div class="stat"><strong>{sum(bool(p['code']) for p in papers):02}</strong><span>已核实官方代码</span></div></div>
<section><div class="section-head"><div><div class="eyebrow">THE FEEDBACK LOOP</div><h2>用一个闭环理解自进化</h2></div><p>本站采用广义定义。区分系统直接改进、改进所需的方法，以及评测基础。</p></div><div class="loop"><div><span class="n">01 / Observe</span><b>观察反馈</b><p>交互、误差、偏好、奖励与环境变化。</p></div><div><span class="n">02 / Diagnose</span><b>识别改进方向</b><p>反思失败，选择数据、记忆或更新策略。</p></div><div><span class="n">03 / Update</span><b>更新系统</b><p>调整训练数据、参数、策略、提示与记忆。</p></div><div><span class="n">04 / Evaluate</span><b>验证并进入下一轮</b><p>用独立反馈检验质量、稳定性与计算代价。</p></div></div><p class="note">这是一种阅读与分类框架；单篇论文可能只覆盖其中一部分。“自监督”或“用了 LLM”本身不构成完整自进化。</p></section>
<section id="taxonomy"><div class="section-head"><div><div class="eyebrow">01 / RESEARCH TRACKS</div><h2>六条研究路线</h2></div><p>按主要改进机制分组；点击路线即可筛选文献。分类表示研究关系，不是论文质量排名。</p></div><div class="taxonomy">{tax}</div></section>
<section id="catalog"><div class="section-head"><div><div class="eyebrow">02 / PAPER LIBRARY</div><h2>从经典到近期进展</h2></div><a class="section-link" href="#scope">查看收录标准 ↗</a></div>
<form class="filters" data-filters role="search"><div class="controls"><label>检索论文、方法或关键词<input type="search" name="q" placeholder="例如：self-improvement、反思、持续学习、RSIR" aria-label="检索论文、方法或关键词"></label><label>发表会议<select name="venue">{options([(v,v) for v in venues],'全部会议')}</select></label><label>年份<select name="year">{options([(y,y) for y in sorted({p['year'] for p in papers},reverse=True)],'全部年份')}</select></label><label>研究路线<select name="category">{options([(k,v[0]) for k,v in CATEGORIES.items()],'全部路线')}</select></label><label>与自进化的关系<select name="relevance">{options(RELEVANCE.items(),'全部关系')}</select></label><label>实现可用性<select name="code"><option value="">不限</option><option value="yes">已核实官方代码</option></select></label></div><div class="toolbar"><button type="button" data-reset>重置</button><button type="button" data-expand>展开详情</button><button type="button" data-collapse>收起详情</button><button type="button" data-export>导出当前清单 JSON ↓</button><output class="count-output" data-count aria-live="polite">显示 {len(papers)} / {len(papers)} 条</output></div></form><noscript>当前显示完整论文清单。启用 JavaScript 后可使用搜索、筛选与导出。</noscript><p class="note">默认按年份倒序，同年优先显示直接闭环工作。近期代表作的长期影响仍待时间检验；收录理由是基于来源的编辑判断。</p>
<div data-entries>{''.join(paper_html(p) for p in papers)}</div><div class="empty" data-empty hidden>没有符合条件的论文。请减少关键词或重置筛选。</div></section>
<section id="reading"><div class="section-head"><div><div class="eyebrow">03 / READING PATHS</div><h2>按研究问题开始阅读</h2></div><p>这些是建议阅读路径，不表示后续工作都直接建立在前一篇之上。</p></div><div class="reading"><div><h3>模型如何产生新的训练信号？</h3><p>先了解蒸馏与自举监督，再阅读数据生成和系统自纠正；检验改进是否超出额外训练本身。</p>{references(['ranking-distillation-2018','buir-2021','RSIR'])}</div><div><h3>怎样从交互中改善下一次决策？</h3><p>从探索与回报建模进入智能体反馈；关注环境真实性、反馈成本以及跨轮次变化。</p>{references(['linucb-2010','slateq-2019','AgentCF','BiLLP'])}</div><div><h3>怎样证明系统真的在变好？</h3><p>先理解曝光偏差与反事实评估，再看持续自纠正；最终回到冻结测试集、预算和独立验证。</p>{references(['recommendations-as-treatments-2016','slate-ope-2017','reloop-2022'])}</div></div></section>
<section id="questions"><div class="section-head"><div><div class="eyebrow">04 / OPEN QUESTIONS</div><h2>读完论文之后，继续追问什么？</h2></div></div><div class="principles"><div><h3>01 · 改进的信号来自哪里？</h3><p>真实用户、固定教师、模拟用户与自我打分的可信度不同。模型认可自己的答案，不能单独证明外部推荐质量提高。</p></div><div><h3>02 · 收益能否穿过多轮迭代？</h3><p>看每一轮的结果、退化和停止条件。单轮提升与持续自进化是不同强度的证据。</p></div><div><h3>03 · 改进是否值得其代价？</h3><p>将生成、筛选、训练和评估全部计入预算，并设置等训练步数、等样本曝光和等成本的对照。</p></div><div><h3>04 · 适应与遗忘如何平衡？</h3><p>同时检验未来窗口的表现与历史用户、长尾物品上的变化；平均准确率可能掩盖持续退化。</p></div></div><p class="note">以上为本站的研究问题与评测建议，相关方法和证据见各论文条目。</p><a class="btn" href="{e(BENCH_PROTOCOL_URL)}">查看四类评测协议 →</a></section>
<section id="scope" class="scope"><h2>收录标准与证据边界</h2><p><b>主题范围：</b>广义推荐系统自进化：自主改进、反馈记忆、自训练与合成监督、持续适应、探索与策略学习。直接工作必须包含反馈驱动的更新；支撑方法与经典骨干分别标记，不能据此声称它们实现了系统级自主自进化。</p><p><b>发表范围：</b>采用领域顶会精选口径，覆盖推荐、检索、数据挖掘与机器学习重要会议，不统一标成 CCF A。优先正式研究论文；少量具有直接研究价值的短文、Perspective 或工业工作单独标明发表类型。没有已核实会议录用依据的预印本不进入清单。</p><p><b>时间与影响：</b>重点检索 2023—2026，回溯相关经典。经典优先考虑其方法沿用与基线价值；新作依据问题、方法代表性和可核实发表记录收录。没有以未经核验的引用量或 GitHub 星数代替学术影响。</p><p><b>核验方式：</b>以会议、出版社、作者论文与官方仓库核对题录和方法。每篇附来源与限制；摘要级核对不会写成独立复现，论文报告的效果也不会自动进入本站统一评测榜单。</p><p><b>覆盖限制：</b>这是精选导航，尚未穷尽所有会议论文集。这里的篇数表示当前收录量，不能当作领域论文产量。核对截至 {e(CFG['asof'])}。</p><p>参照 <a href="https://opensdc-org.github.io/survey/">OpenSDC Survey</a> 的文献组织方式；本文献库与其研究主题独立。欢迎通过 {link(CFG['repo_url']+'/issues','GitHub Issues')} 提交遗漏与勘误。</p></section>
<footer class="footer"><span>RSI Atlas / Survey<br>中文整理 · 英文原题 · 文献资料核对 {e(CFG['asof'])}</span><span>维护者 {e(CFG['owner'])} · 公开文献精选<br>论文版权归原作者与出版方所有</span><a href="#top">回到顶部 ↑</a></footer></main></div><script id="catalog-data" type="application/json">{payload}</script></body></html>'''
(ROOT/'index.html').write_text(html)
(ROOT/'data'/'papers.json').write_text(json.dumps(papers,ensure_ascii=False,indent=2)+'\n')
(ROOT/'assets'/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#172e2a"/><path d="M45 23a17 17 0 1 0 3 17M45 13v12H33" fill="none" stroke="#e7eee6" stroke-width="4"/><circle cx="32" cy="32" r="4" fill="#d8a074"/></svg>')
print(f'Built RSI Survey: {len(papers)} papers / {len(venues)} venues / {sum(bool(p["code"]) for p in papers)} official code links')
