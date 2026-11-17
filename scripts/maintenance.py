"""Generate a small, offline-readable release history for either RSI site."""
import json
from html import escape


def write_changelog(root, config):
    e = lambda value: escape(str(value), quote=True)
    survey = 'recent_start' in config
    label = 'Survey' if survey else 'Bench'
    other = 'Bench' if survey else 'Survey'
    other_url = config['bench_url'] if survey else config['survey_url']
    updates = json.loads((root / 'data/changelog.json').read_text())['updates']
    entries = []
    for update in updates:
        assert update['date'] and update['version'] and update['items']
        items = ''.join(f'<li>{e(item)}</li>' for item in update['items'])
        entries.append(f'<section class="protocol" id="v{e(update["version"])}"><div class="eyebrow"><time datetime="{e(update["date"])}">{e(update["date"])}</time> / v{e(update["version"])}</div><h2>{e(update["title"])}</h2><ul>{items}</ul></section>')
    template = 'paper.yml' if survey else 'resource.yml'
    suggest = '推荐论文' if survey else '推荐资源'
    repo = config['repo_url']
    html = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>更新记录 · RSI {label}</title><meta name="description" content="RSI {label} 的内容调整、功能更新与维护记录。"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/styles.css"></head><body id="top"><a class="skip" href="#main">跳到正文</a><div class="layout"><aside class="sidebar"><a class="brand" href="index.html">RSI Atlas<span class="mark">SELF-EVOLVING RECOMMENDATION</span></a><div class="switch"><a class="active" href="index.html">{label}</a><a href="{e(other_url)}">{other} ↗</a></div><nav aria-label="维护导航"><div class="nav-label">MAINTENANCE</div><a href="index.html#catalog">返回目录</a><a href="changelog.html" aria-current="page">更新记录</a><a href="{e(repo)}/issues/new?template={template}">{suggest} ↗</a><a href="{e(repo)}/issues/new?template=correction.yml">报告错误 ↗</a></nav></aside><main class="main" id="main"><div class="topline"><a class="mobile-brand" href="index.html">RSI Atlas</a><span class="edition">{label.upper()} / CHANGELOG</span><nav aria-label="站点入口"><a href="index.html">{label}</a><a href="{e(other_url)}">{other}</a><a href="{e(repo)}">GitHub ↗</a></nav></div><header class="hero"><div class="eyebrow">WHAT CHANGED</div><h1>更新记录</h1><p class="lead">记录内容取舍与功能变化，方便追踪这个站点如何完善。</p><div class="hero-actions"><a class="btn primary" href="index.html#catalog">返回目录</a><a class="btn" href="{e(repo)}/issues/new?template={template}">{suggest} ↗</a><a class="btn" href="{e(repo)}/issues/new?template=correction.yml">报告错误 ↗</a></div></header>{''.join(entries)}<footer class="footer"><span>RSI Atlas / {label} · 维护者 {e(config['owner'])}</span><a href="{e(repo)}/commits/main/">查看完整提交历史 ↗</a><a href="#top">回到顶部 ↑</a></footer></main></div></body></html>'''
    (root / 'changelog.html').write_text(html, encoding='utf-8')
