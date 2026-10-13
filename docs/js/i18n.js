const STRINGS = {
  en: {
    title: "Agent Benchmarks",
    kicker: "arXiv daily",
    docTitle: "Daily Agent Benchmarks",
    pageTitle: "Daily Agent Benchmarks — New LLM agent benchmarks on arXiv, updated daily",
    archive: "Archive",
    searchLabel: "Search benchmarks",
    searchPlaceholder: "Search titles, abstracts, tags…",
    exactMatch: "Exact / cover match",
    viewField: "By field",
    viewDate: "By date",
    viewHeat: "By citations",
    citations: "citations",
    visitorsPage: "Page views",
    visitorsSite: "visitors",
    backHome: "All benchmarks",
    openArxiv: "Open on arXiv",
    matchExact: "exact title",
    matchCover: "covers query",
    paperPage: "arXiv",
    openField: "Open",
    backFields: "All fields",
    loadMore: "Load more",
    latestInField: "Latest",
    fieldHint: "Use the tabs to filter. Sort the current tab by date or citations.",
    fieldAll: "All",
    sortDate: "By date",
    sortCite: "By citations",
    sortBy: "Sort",
    github: "GitHub",
    githubAria: "Open the GitHub repository",
    themeToggle: "Toggle color theme",
    themeToLight: "Light",
    themeToDark: "Dark",
    heroLead:
      "A once-a-day reading list of new agent benchmarks on arXiv — names, abstracts, links, and a short digest for each announcement day.",
    papers: "papers",
    days: "days",
    latest: "latest drop",
    dailyReport: "Daily report",
    expand: "Read abstract",
    collapse: "Hide abstract",
    pdf: "PDF",
    html: "HTML",
    abs: "Abstract page",
    authors: "Authors",
    searchResults: (n, q) =>
      n === 1 ? `1 result for “${q}”` : `${n} results for “${q}”`,
    noResults: (q) => `No benchmarks matched “${q}”.`,
    empty: "No papers in the index yet. Run the daily updater.",
    loadError: "Could not load the paper index.",
    updated: "Index generated",
    footer:
      "Papers are collected from the arXiv API, kept if they look like agent benchmarks, and grouped by submission date. Ranked search uses BM25 in the browser.",
  },
  zh: {
    title: "Agent Benchmarks",
    kicker: "arXiv 每日",
    docTitle: "每日 Agent Benchmark",
    pageTitle: "每日 Agent Benchmark — arXiv 最新 LLM 智能体评测基准，每日更新",
    archive: "归档",
    searchLabel: "搜索基准",
    searchPlaceholder: "搜索标题、摘要、标签…",
    exactMatch: "精确 / 覆盖匹配",
    viewField: "按领域",
    viewDate: "按日期",
    viewHeat: "按引用热度",
    citations: "次引用",
    visitorsPage: "本页浏览",
    visitorsSite: "位访客",
    backHome: "全部基准",
    openArxiv: "在 arXiv 打开",
    matchExact: "标题精确匹配",
    matchCover: "覆盖查询词",
    paperPage: "arXiv",
    openField: "打开",
    backFields: "全部领域",
    loadMore: "加载更多",
    latestInField: "最近",
    fieldHint: "用页签筛选领域；每个页签都可以按日期或引用排序。",
    fieldAll: "全部",
    sortDate: "按日期",
    sortCite: "按引用",
    sortBy: "排序",
    github: "GitHub",
    githubAria: "打开 GitHub 仓库",
    themeToggle: "切换配色",
    themeToLight: "浅色",
    themeToDark: "深色",
    heroLead:
      "每日一次整理 arXiv 上新出现的 Agent Benchmark：名称、摘要、链接，以及当天的简报。",
    papers: "篇论文",
    days: "个日期",
    latest: "最近更新",
    dailyReport: "每日简报",
    expand: "展开摘要",
    collapse: "收起摘要",
    pdf: "PDF",
    html: "HTML",
    abs: "摘要页",
    authors: "作者",
    searchResults: (n, q) => `“${q}” 共 ${n} 条结果`,
    noResults: (q) => `没有与“${q}”匹配的基准。`,
    empty: "索引中还没有论文。请先运行每日更新脚本。",
    loadError: "无法加载论文索引。",
    updated: "索引生成时间",
    footer:
      "论文来自 arXiv API，仅保留 Agent Benchmark 相关条目，按投稿日期分组。网页内搜索使用 BM25。",
  },
};

const SYNONYMS = {
  智能体: ["agent", "agents", "agentic"],
  代理: ["agent", "agents"],
  多智能体: ["multi-agent", "multiagent", "multiagents"],
  基准: ["benchmark", "benchmarks"],
  评测: ["evaluation", "eval", "benchmark"],
  评估: ["evaluation", "eval"],
  工具: ["tool", "tools", "tool-use"],
  网页: ["web", "browser"],
  代码: ["coding", "code", "software"],
  安全: ["safety"],
  具身: ["embodied", "robot"],
  规划: ["planning"],
  记忆: ["memory"],
  对话: ["dialogue", "dialog", "conversation"],
  多模态: ["multimodal", "vision"],
  手机: ["mobile", "android"],
  计算机使用: ["computer-use", "computer"],
  递归: ["recursive", "rsi", "self-improvement"],
  自我改进: ["self-improvement", "rsi", "ai4ai"],
  办公: ["office", "workplace", "workarena"],
  职场: ["workplace", "professional", "office"],
};

const FIELD_LABELS = {
  all: { en: "All", zh: "全部" },
  rsi: { en: "RSI / AI4AI", zh: "RSI / AI4AI" },
  workplace: { en: "Work / office", zh: "职场 / 办公" },
  coding: { en: "Coding / SWE", zh: "代码 / 软件工程" },
  web: { en: "Web & browser", zh: "网页 / 浏览器" },
  mobile: { en: "Mobile", zh: "移动端" },
  "computer-use": { en: "GUI / computer use", zh: "GUI / 计算机使用" },
  "tool-use": { en: "Tool use", zh: "工具使用" },
  "multi-agent": { en: "Multi-agent", zh: "多智能体" },
  safety: { en: "Safety", zh: "安全" },
  science: { en: "Science & research", zh: "科学 / 科研" },
  embodied: { en: "Embodied / robotics", zh: "具身 / 机器人" },
  conversation: { en: "Dialogue", zh: "对话" },
  multimodal: { en: "Multimodal", zh: "多模态" },
  other: { en: "General", zh: "综合 / 其他" },
};

const FIELD_BLURBS = {
  all: {
    en: "Every agent benchmark in the index.",
    zh: "索引中的全部 Agent Benchmark。",
  },
  rsi: {
    en: "Recursive self-improvement, AI4AI, and agents that train or redesign other AI systems.",
    zh: "递归自我改进、AI4AI，以及改进或设计其他 AI 系统的智能体评测。",
  },
  workplace: {
    en: "Office, professional, and economically grounded agent workflows — ALE, WorkArena, TheAgentCompany.",
    zh: "办公、职场与经济价值相关的 agent 评测，如 ALE、WorkArena、TheAgentCompany。",
  },
  coding: { en: "Software engineering agents and repository-level coding benches.", zh: "软件工程与仓库级代码智能体基准。" },
  web: { en: "Browser and website agents.", zh: "网页与浏览器智能体。" },
  mobile: { en: "Android / iOS device agents.", zh: "手机端智能体。" },
  "computer-use": { en: "Desktop, GUI, and computer-use agents.", zh: "桌面、GUI 与计算机使用智能体。" },
  "tool-use": { en: "Tool calling, APIs, and MCP.", zh: "工具调用、API 与 MCP。" },
  "multi-agent": { en: "Societies of agents and debate setups.", zh: "多智能体协作与辩论。" },
  safety: { en: "Safety, jailbreaks, and malicious skills.", zh: "安全、越狱与恶意技能。" },
  science: { en: "Scientific and research agents.", zh: "科学与科研智能体。" },
  embodied: { en: "Robots and embodied environments.", zh: "机器人与具身环境。" },
  conversation: { en: "Dialogue and customer-service agents.", zh: "对话与客服智能体。" },
  multimodal: { en: "Vision-language and mixed-media agents.", zh: "多模态智能体。" },
  other: { en: "Everything that does not sit cleanly in a narrower field.", zh: "尚未归入更细门类的基准。" },
};

function fieldBlurb(id, lang) {
  const row = FIELD_BLURBS[id] || FIELD_BLURBS.other;
  return row[lang === "zh" ? "zh" : "en"];
}

function fieldLabel(id, lang) {
  return (FIELD_LABELS[id] || FIELD_LABELS.other)[lang === "zh" ? "zh" : "en"];
}

function t(lang, key, ...args) {
  const table = STRINGS[lang] || STRINGS.en;
  const value = table[key] ?? STRINGS.en[key] ?? key;
  return typeof value === "function" ? value(...args) : value;
}

function applyStaticI18n(lang) {
  document.documentElement.lang = lang === "zh" ? "zh-Hans" : "en";
  document.title = t(lang, "pageTitle");
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(lang, el.getAttribute("data-i18n"));
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.setAttribute("placeholder", t(lang, el.getAttribute("data-i18n-placeholder")));
  });
  document.querySelectorAll("[data-i18n-aria]").forEach((el) => {
    el.setAttribute("aria-label", t(lang, el.getAttribute("data-i18n-aria")));
  });
}

function formatDay(date, lang) {
  const [y, m, d] = date.split("-").map(Number);
  if (lang === "zh") return `${y}年${m}月${d}日`;
  const dt = new Date(Date.UTC(y, m - 1, d));
  return dt.toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  });
}

function formatStamp(iso, lang) {
  if (!iso) return "";
  const dt = new Date(iso);
  if (Number.isNaN(dt.getTime())) return iso;
  return dt.toLocaleString(lang === "zh" ? "zh-CN" : "en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}
