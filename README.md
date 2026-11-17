# RSI Survey · 推荐系统自进化研究图谱

推荐系统自进化领域顶会文献精选，重点覆盖 2023–2026 年，回溯经典基础。采用广义闭环定义，分别标注直接闭环、支撑方法与经典基础。不是仅围绕 RSIR 的专题，也不将所有论文统一标为 CCF A。

- 网站：<https://LiHaoxu.github.io/rsi-survey/>
- 配套评测站：<https://LiHaoxu.github.io/rsi-bench/>
- 文献核对日期：2026-11-17
- 来源文件：`data/recent.json`、`data/classics.json`
- 生成文件：`index.html`、`data/papers.json`

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

`bib_authors` 是核实过的完整 BibTeX 作者列表。如果没有该字段，网页下载的是文本引文，避免把 `et al.` 当作完整作者列表。

更新数据后运行构建与检查，连同生成文件提交。所有实验结果必须带来源；论文自报结果不能伪装成本站统一协议下的复现。详细边界见网页“收录标准”。

## 发布

`.github/workflows/pages.yml` 在 `main` 更新时重新构建、检查并部署 GitHub Pages。仓库 Settings → Pages 的 Source 应为 GitHub Actions。只上传网页、资源与公开 JSON；工作区中的私人研究文件不属于这个仓库。

## 致谢

文献组织参考 [OpenSDC Survey](https://opensdc-org.github.io/survey/)，本项目按推荐系统自进化主题重新组织内容与界面。论文及第三方资源的权利归原作者和发布方；本站仅提供题录、原创概括和出处链接。
