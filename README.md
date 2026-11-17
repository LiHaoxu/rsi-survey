# RSI Survey · 推荐系统自进化研究图谱

推荐系统自进化领域顶会文献精选，重点覆盖 2022–2026 年，回溯经典基础。采用广义闭环定义，分别标注直接闭环、支撑方法与经典基础。不是仅围绕 RSIR 的专题，也不将所有论文统一标为 CCF A。

- 网站：<https://LiHaoxu.github.io/rsi-survey/>
- 配套评测站：<https://LiHaoxu.github.io/rsi-bench/>
- 文献核对日期：2026-11-17
- 来源文件：`data/recent.json`、`data/classics.json`
- 生成文件：`index.html`、`data/papers.json`
- 本轮筛选记录：`data/selection-review.json`，记录新增、移出、暂缓候选与取舍依据。

当前精选 39 篇：25 篇发表于 2022–2026，14 篇为必要经典与方法前史。本轮新增 9 篇、移出 2 篇。主要补齐持续用户建模、增量图推荐、个性化知识保留、提示优化、知识修正、长期反馈和自引导去噪；不按年度配额或总篇数凑清单。

## 本地构建与阅读

需要 Python 3.9+，无第三方依赖。

```sh
python3 scripts/build.py
python3 scripts/check.py
```

直接打开 `index.html` 即可离线阅读和筛选。网站不依赖 CDN、外部字体或网络 API；打开论文和代码链接时才访问外部网站。将 `rsi-survey` 与 `rsi-bench` 放在同一父目录，即可在本地互相跳转。

## 内容维护

每条论文记录的 `id` 为稳定锚点；`category` 表示主路线，`relevance` 区分 `direct`、`enabling`、`foundation`。`publication_type` 默认 `full`，短文等必须写明。

每条须有题名、年份、会议、作者、问题、方法、反馈环节、证据、局限、收录理由和第一方来源。`code` 只填写可确认属于原作者的代码；无法确认时留空。影响力不以臆造的引文数或未经核实的星数描述。新作称近期代表作，不能自动称经典。

时间范围由 `config.json` 的 `recent_start` / `recent_end` 控制，按正式会议发表年份归档。`recent.json` 存放五年范围内条目，`classics.json` 仅放更早的必要前史；网页的年份筛选同时支持“近五年”和“经典前史”。每次调整范围或清单后，应同步更新本说明中的统计及筛选记录。

优先纳入有后续基线沿用、关键机制代表性或真实系统验证依据的工作。同类方法不重复堆叠，标题中的 self、LLM、自监督或顶会发表本身均不足以入选。移出条目在网页收录标准中保留说明与原锚点；移出是主题覆盖度判断，不等于否定论文质量。

`bib_authors` 是核实过的完整 BibTeX 作者列表。如果没有该字段，网页下载的是文本引文，避免把 `et al.` 当作完整作者列表。

更新数据后运行构建与检查，连同生成文件提交。所有实验结果必须带来源；论文自报结果不能伪装成本站统一协议下的复现。详细边界见网页“收录标准”。

## 发布

`.github/workflows/pages.yml` 在 `main` 更新时重新构建、检查并部署 GitHub Pages。仓库 Settings → Pages 的 Source 应为 GitHub Actions。只上传网页、资源与公开 JSON；工作区中的私人研究文件不属于这个仓库。

## 致谢

文献组织参考 [OpenSDC Survey](https://opensdc-org.github.io/survey/)，本项目按推荐系统自进化主题重新组织内容与界面。论文及第三方资源的权利归原作者和发布方；本站仅提供题录、原创概括和出处链接。

## v1.1 浏览与关联

目录默认使用紧凑列表；可切换详细卡片，并按年份或标题排序。年份、会议、路线、代码条件、视图和排序保存在 URL 中，适合分享筛选后的清单。论文永久链接会揭示被筛选隐藏的条目。论文详情中的 Bench 入口分为已核验资源关联与本站建议协议；实现收录不自动表示原论文使用该工具。

`data/connections.json` 是两个仓库各自保存的同一份关联快照。`papers`、`resources`、`protocols` 存放公开题录和入口；`links` 中 `uses` 表示已核验的论文使用，`implements` 表示作者实现或后续工具收录，`suggested` 表示本站建议；`protocol_links` 全部是建议，不能当作论文事实。事实关联必须带 `sources` 与 `locator`，不同数据版本不得按简称合并。修改关联时同步两个仓库，并核对双方条目 ID；独立构建不依赖另一个仓库的网络可用性。

维护入口：网页上的推荐与纠错按钮打开 GitHub Issue 表单；不会直接发布内容。`data/changelog.json` 保存更新记录，由 `scripts/maintenance.py` 生成 `changelog.html`，随主构建运行。

每次更新后执行：

```sh
python3 scripts/build.py
python3 scripts/check_site.py
```

Survey 另执行 `python3 scripts/check.py`。`check_site.py` 核验所有页面的站内文件、锚点、关联引用和题录快照；两个仓库在本地并排时还会核验跨站目标，CI 单独构建时允许兄弟仓库不存在。

`Review external links` 工作流每周日 08:00 UTC 运行，也可以在 Actions 手动触发。它检查页面里的公共来源链接，把状态摘要写入运行页面，并保存 JSON 报告 30 天。403、429、网络超时与疑似失效分开记录，供维护者核查；不会自动删论文、修改来源或发送 Issue。可在本地运行 `python3 scripts/check_external_links.py --output /tmp/rsi-link-report.json`。
