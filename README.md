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
