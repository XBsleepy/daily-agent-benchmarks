# Daily Agent Benchmarks

每日从 [arXiv](https://arxiv.org) 收集 **Agent Benchmark** 论文，整理成可部署到 GitHub Pages 的静态站点。

站点按投稿日期倒序展示：名称、作者、摘要、分类、PDF / HTML 链接；每一天有一份中英双语简报；浏览器内用 **BM25** 做排序搜索。

## 这个仓库做什么

1. **每天跑一次**（GitHub Actions，也可本地手动跑）调用 arXiv API。
2. **只保留 Agent Benchmark**：先用 agent + benchmark 相关查询召回，再用关键词打分过滤（LLM agent、web/GUI/coding agent、tool-use、computer-use 等）。不收录普通 RL agent、试剂 / 病原体等无关用法。
3. **合并进索引** `docs/data/index.json`，按 `published` 日期分组。
4. **生成当日简报**（无需付费模型）：主题统计 + 高分论文的摘要首句，中英各一份。
5. **GitHub Pages** 读取这份 JSON 渲染页面。搜索在浏览器里完成，不依赖后端。

## 本地更新

需要 Python 3.11+，只用标准库。

```bash
python scripts/update.py --backfill 45
```

之后的增量更新（默认回看 4 天，避免时区漏检）：

```bash
python scripts/update.py --days 4
```

只按当前规则重过滤已有索引（不访问网络）：

```bash
python scripts/update.py --reclassify
```

清空后按本次抓取重建（改分类器后建议用一次）：

```bash
python scripts/update.py --replace --backfill 45
```

第一次跑如果索引还是空的，脚本会自动回看约 45 天。

本地预览：

```bash
python -m http.server 8080 --directory docs
```

打开 http://127.0.0.1:8080 。

## 发布到 GitHub.io

1. 把仓库推到 GitHub。
2. **Settings → Pages → Build and deployment**
   - Source: **Deploy from a branch**
   - Branch: `main`（或 `master`），folder: **/docs**
3. 打开 **Actions**，确认 `Daily arXiv update` 工作流已启用（fork 仓库需要手动打开 scheduled workflow）。
4. 站点地址：
   - 项目页：`https://<user>.github.io/daily-agent-benchmarks/`
   - 若仓库名是 `<user>.github.io`，则在根路径。

工作流在 [arXiv 每日公告](https://info.arxiv.org/help/availability.html)（周日到周四 20:00 美国东部时间）之后跑：UTC 00:25、01:25、03:30，以及 08:00 / 14:00 补跑（周一到周五）。对应北京时间约 08:25、09:25、11:30、16:00、22:00。请求超时会自动重试。有新增就会提交 `docs/data/`。 GitHub 的 cron 在不活跃仓库上经常晚几小时，补跑就是为了兜住。

## 网页能力

| 能力 | 做法 |
| --- | --- |
| 每日简报 | 更新脚本里抽主题、写中英摘要，随 JSON 发布。页面按天展示。 |
| BM25 搜索 | 前端对标题 / 摘要 / 标签建索引。中文查询会先映射到 agent、benchmark 等英文同义词。按 `/` 聚焦搜索框。 |
| 中 / 英 | 界面文案切换；论文正文保持 arXiv 原文（几乎都是英文）。简报有中英两套。 |

更长的中文摘要可以以后接 LLM；当前设计刻意不依赖 API key，这样 GitHub Actions 才能稳定空跑。

## 过滤规则（简要）

**会留下**：标题或摘要里同时有较强的 agent 信号（如 LLM / language / web / GUI / coding agent、agentic、tool-use、computer-use）和评测信号（benchmark、leaderboard、testbed、evaluation）。

**会丢掉**：reagent、pathogen、travel agent、user-agent，以及标题明显是强化学习、又没有 LLM/tool agent 证据的论文。

规则在 `scripts/config.py` 和 `scripts/classify.py`，可以按误伤 / 漏检改关键词。

## 目录

```
scripts/          抓取、过滤、简报、写 JSON
docs/             GitHub Pages 站点
docs/data/        索引与按日切片
.github/workflows 每日定时更新
```
