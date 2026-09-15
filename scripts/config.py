"""Keyword lists, categories, and theme taxonomy for agent-benchmark filtering."""

from __future__ import annotations

ARXIV_API = "https://export.arxiv.org/api/query"
# RSS stays available when export.arxiv.org API rate-limits GitHub Actions IPs.
ARXIV_RSS = (
    "https://rss.arxiv.org/rss/"
    + "+".join(("cs.AI", "cs.CL", "cs.LG", "cs.MA", "cs.SE", "cs.HC", "cs.RO", "cs.CV", "cs.IR", "cs.CR"))
)
USER_AGENT = (
    "daily-agent-benchmarks/1.0 "
    "(https://github.com/XBsleepy/daily-agent-benchmarks; arxiv tracker; polite bot)"
)

# Computer-science categories where agent benchmarks actually appear.
ARXIV_CATEGORIES = (
    "cs.AI",
    "cs.CL",
    "cs.LG",
    "cs.MA",
    "cs.SE",
    "cs.HC",
    "cs.RO",
    "cs.CV",
    "cs.IR",
    "cs.CR",
)

# Keep the Lucene query short. Date filtering happens locally after sort.
# Precision is applied in classify.py.
SEARCH_QUERIES = (
    '(ti:benchmark OR ti:bench OR ti:arena OR ti:leaderboard OR ti:testbed) AND (ti:agent OR ti:agentic OR abs:"llm agent" OR abs:"language agent" OR abs:"autonomous agent" OR abs:agentic)',
    'ti:"agent benchmark" OR ti:"agents benchmark" OR ti:"agentic benchmark" OR ti:"benchmarking agents" OR ti:"benchmarking language agents"',
    'all:"benchmark for" AND (all:"llm agent" OR all:"language agents" OR all:"autonomous agents" OR all:"ai agents")',
    # Catches named evals whose title has "Agents" but not "Bench" (e.g. Agents' Last Exam).
    '(ti:agent OR ti:agents) AND abs:benchmark AND (cat:cs.AI OR cat:cs.CL OR cat:cs.LG OR cat:cs.MA)',
)

REQUEST_TIMEOUT_S = 60
REQUEST_RETRIES = 4
REQUEST_GAP_S = 5.0
# arXiv rate-limits shared GitHub Actions IPs hard; wait longer than the usual gap.
RATE_LIMIT_FLOOR_S = 45.0
RATE_LIMIT_MAX_S = 120.0
QUERY_GAP_S = 8.0
PAGE_SIZE = 100
MAX_PAGES = 30
ARCHIVE_START = "2026-01-01"

# --- classification -------------------------------------------------------

STRONG_AGENT_PATTERNS = (
    r"\bllm[- ]agents?\b",
    r"\blanguage agents?\b",
    r"\bautonomous agents?\b",
    r"\bai agents?\b",
    r"\bagentic\b",
    r"\bmulti[- ]agents?\b",
    r"\bmultiagents?\b",
    r"\bweb agents?\b",
    r"\bgui agents?\b",
    r"\bcoding agents?\b",
    r"\bsoftware agents?\b",
    r"\bresearch agents?\b",
    r"\bcomputer[- ]use\b",
    r"\bcomputer use agents?\b",
    r"\btool[- ]use\b",
    r"\btool[- ]using\b",
    r"\btool calling\b",
    r"\bfunction calling\b",
    r"\bgeneral ai assistants?\b",
    r"\bai assistants?\b",
    r"\bembodied agents?\b",
    r"\bbrowser agents?\b",
    r"\bmobile agents?\b",
    r"\bos agents?\b",
    r"\bdigital agents?\b",
    r"\binteractive agents?\b",
)

WEAK_AGENT_PATTERNS = (
    r"\bagents?\b",
)

STRONG_BENCH_PATTERNS = (
    r"\bbenchmarks?\b",
    r"\bleaderboards?\b",
    r"\btestbeds?\b",
    r"\btest[- ]beds?\b",
    r"\barenas?\b",
    r"\beval suites?\b",
    r"\bevaluation suites?\b",
    r"\bchallenge tracks?\b",
)

WEAK_BENCH_PATTERNS = (
    r"\bevaluations?\b",
    r"\bevals?\b",
    r"\btest[- ]time\b",
    r"\bdatasets?\b",
    r"\btasks suites?\b",
)

NEGATIVE_PATTERNS = (
    r"\breagent\b",
    r"\bpathogen\b",
    r"\bchemical agents?\b",
    r"\bbiolog(?:ical|y) agents?\b",
    r"\btravel agents?\b",
    r"\breal[- ]estate agents?\b",
    r"\binsurance agents?\b",
    r"\bsecret agents?\b",
    r"\buser[- ]agents?\b",
    r"\bprincipal[- ]agent\b",
    r"\bmarkov decision\b",
    r"\bmulti[- ]agent reinforcement learning\b",
    r"\bmarl\b",
)

# Title-only RL papers with a generic "agent" mention are usually not
# LLM / tool-use agent benchmarks.
RL_TITLE_PATTERNS = (
    r"\breinforcement learning\b",
    r"\bq[- ]learning\b",
    r"\bpolicy gradient\b",
)

# Named *Bench / *Arena style titles, plus well-known suites.
TITLE_BENCH_PATTERNS = (
    r"\bbenchmarking\b",
    r"\bbenchmarks?\s+(?:for|of)\b",
    r"\bagents?\s+benchmarks?\b",
    r"\ba(?:n)?\s+(?:new\s+)?benchmark\b",
    r"\b[a-z][\w-]*[-_]?benchs?\b",
    r"\b[a-z][\w-]*arenas?\b",
    r"\bleaderboards?\b",
    r"\btest[- ]?beds?\b",
    r"\beval(?:uation)? suites?\b",
    r"\bbench\b",
    r"\blast exam\b",
    r"\bagents?'? exam\b",
)

INTRO_BENCH_PATTERNS = (
    r"\b(?:introduce|present|propose|release|construct|establish)\b.{0,100}\bbenchmarks?\s+for\b.{0,70}\bagents?\b",
    r"\b(?:introduce|present|propose|release|construct)\b.{0,80}\b(?:testbed|leaderboard|arena)\b.{0,60}\bagents?\b",
    r"\b(?:introduce|present|propose|release|construct|establish)\b.{0,140}\ba(?:n)?\s+(?:new\s+)?benchmark\b",
    r"\bbenchmark(?:s)? designed to (?:evaluate|test|assess|measure)\b.{0,80}\bagents?\b",
    r"\ba benchmark\b.{0,100}\b(?:evaluate|evaluating|evaluation of)\b.{0,40}\bagents?\b",
)

NAMED_BENCH_PATTERNS = (
    r"\bswe[- ]?bench\b",
    r"\bwebarena\b",
    r"\bvisualwebarena\b",
    r"\bosworld\b",
    r"\bandroidworld\b",
    r"\bworkarena\b",
    r"\bagentbench\b",
    r"\btoolbench\b",
    r"\btau[- ]?bench\b",
    r"\bbrowsecomp\b",
    r"\btheagentcompany\b",
    r"\bagents?'? last exam\b",
    r"\bale\b.{0,40}\b(?:benchmark|exam|agent)",
    r"\b(?:benchmark|exam|agent).{0,40}\bale\b",
    r"\bgaia\b.{0,40}\b(?:benchmark|assistant|agent)",
    r"\b(?:benchmark|assistant|agent).{0,40}\bgaia\b",
)

THEMES: dict[str, tuple[str, ...]] = {
    "web": (r"\bweb agents?\b", r"\bbrowser\b", r"\bwebarena\b", r"\bhtml\b", r"\bwww\b"),
    "gui": (r"\bgui\b", r"\bscreenshot\b", r"\bdesktop\b", r"\bosworld\b", r"\bvisual grounding\b"),
    "coding": (
        r"\bcoding agents?\b",
        r"\bsoftware engineering\b",
        r"\bswe[- ]bench\b",
        r"\bgitHub issues\b",
        r"\bcode generation\b",
        r"\brepository\b",
    ),
    "tool-use": (
        r"\btool[- ]use\b",
        r"\btool[- ]using\b",
        r"\bfunction calling\b",
        r"\bapi[- ]bank\b",
        r"\btools?\b",
    ),
    "multi-agent": (r"\bmulti[- ]agents?\b", r"\bmultiagents?\b", r"\bsociety of agents\b"),
    "computer-use": (r"\bcomputer[- ]use\b", r"\bos agents?\b", r"\bdesktop agents?\b"),
    "embodied": (r"\bembodied\b", r"\brobot\b", r"\bsimulation environment\b"),
    "safety": (r"\bsafety\b", r"\bjailbreak\b", r"\bharmless\b", r"\brisk\b", r"\brobust"),
    "memory": (r"\blong[- ]term memory\b", r"\bmemory\b", r"\bcontext window\b"),
    "planning": (r"\bplanning\b", r"\breasoning\b", r"\breact\b"),
    "research": (r"\bresearch agents?\b", r"\bliterature\b", r"\bscientific discovery\b"),
    "conversation": (r"\bdialog(?:ue)?\b", r"\bcustomer service\b", r"\btau[- ]bench\b"),
    "multimodal": (r"\bmultimodal\b", r"\bvision[- ]language\b", r"\bvlm\b"),
    "mobile": (r"\bandroid\b", r"\bios\b", r"\bmobile agents?\b"),
    "science": (r"\bchemistry\b", r"\bbiolog", r"\bscientif", r"\blab\b"),
    "rsi": (
        r"\brecursive self[- ]improv",
        r"\bai4ai\b",
        r"\bai[- ]for[- ]ai\b",
        r"\bself[- ]improving agents?\b",
    ),
    "workplace": (
        r"\bagents?'? last exam\b",
        r"\btheagentcompany\b",
        r"\bworkarena\b",
        r"\bworkplace\b",
        r"\bknowledge work\b",
        r"\beconomically valuable\b",
    ),
}

# Match title+abstract first so ALE / AI4AI are not buried in General.
FIELD_PRIORITY_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "rsi",
        (
            r"\brecursive self[- ]improv",
            r"\bai4ai\b",
            r"\bai[- ]for[- ]ai\b",
            r"\bself[- ]improving agents?\b",
            r"\bself[- ]improvement\b.{0,50}\b(?:llm|agent|model|ai)\b",
            r"\bautomated (?:ai|ml) (?:research|scientist|engineering)\b",
            r"\brsi\b.{0,40}\b(?:bench|agent|improv|self)",
        ),
    ),
    (
        "workplace",
        (
            r"\bagents?'? last exam\b",
            r"\btheagentcompany\b",
            r"\bworkarena\b",
            r"\boffice(?:bench| agents?| work| tasks?| automation)\b",
            r"\bworkplace\b",
            r"\bknowledge work\b",
            r"\bwhite[- ]collar\b",
            r"\beconomically valuable\b",
            r"\bprofessional (?:workflow|workflows|domains?|tasks?|occupation)",
            r"\benterprise (?:agents?|workflow)",
            r"\boccupational\b",
            r"\bonet\b",
            r"\bo\*net\b",
            r"\bindustry clusters?\b",
            r"\breal[- ]world (?:business|office|professional)\b",
        ),
    ),
)

# Title cues beat generic abstract tags like "tools".
FIELD_TITLE_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("rsi", (r"\bai4ai\b", r"\brsi\b", r"\bself[- ]improv")),
    ("workplace", (r"\blast exam\b", r"\bworkarena\b", r"\boffice(?:bench|\b)", r"\bworkplace\b")),
    ("coding", (r"\bcoding agents?\b", r"\bswe[- ]?bench\b", r"\bsoftware agents?\b", r"\brepository\b")),
    ("web", (r"\bweb agents?\b", r"\bwebarena\b", r"\bbrowser agents?\b")),
    ("mobile", (r"\bmobile agents?\b", r"\bandroid\b", r"\bios agents?\b")),
    ("computer-use", (r"\bgui agents?\b", r"\bcomputer[- ]use\b", r"\bosworld\b", r"\bdesktop agents?\b")),
    ("multi-agent", (r"\bmulti[- ]agents?\b", r"\bmultiagents?\b")),
    ("safety", (r"\bsafety\b", r"\bjailbreak\b", r"\bmalicious\b", r"\bharmless\b")),
    ("science", (r"\bscientif", r"\bresearch agents?\b")),
    ("embodied", (r"\bembodied\b", r"\brobots?\b", r"\buav\b")),
    ("conversation", (r"\bdialog(?:ue)?\b", r"\bcustomer support\b", r"\bcustomer service\b")),
    ("multimodal", (r"\bmultimodal\b", r"\bvision[- ]language\b")),
    ("tool-use", (r"\btool[- ]use\b", r"\bfunction calling\b", r"\bmcp\b")),
)

FIELD_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("rsi", ("rsi",)),
    ("workplace", ("workplace",)),
    ("coding", ("coding",)),
    ("web", ("web",)),
    ("mobile", ("mobile",)),
    ("computer-use", ("gui", "computer-use")),
    ("multi-agent", ("multi-agent",)),
    ("embodied", ("embodied",)),
    ("conversation", ("conversation",)),
    ("multimodal", ("multimodal",)),
    ("safety", ("safety",)),
    ("tool-use", ("tool-use",)),
    ("science", ("science", "research")),
)

FIELD_LABELS = {
    "rsi": {"en": "RSI / AI4AI", "zh": "RSI / AI4AI"},
    "workplace": {"en": "Work / office", "zh": "职场 / 办公"},
    "coding": {"en": "Coding / SWE", "zh": "代码 / 软件工程"},
    "web": {"en": "Web & browser", "zh": "网页 / 浏览器"},
    "mobile": {"en": "Mobile", "zh": "移动端"},
    "computer-use": {"en": "GUI / computer use", "zh": "GUI / 计算机使用"},
    "tool-use": {"en": "Tool use", "zh": "工具使用"},
    "multi-agent": {"en": "Multi-agent", "zh": "多智能体"},
    "safety": {"en": "Safety", "zh": "安全"},
    "science": {"en": "Science & research", "zh": "科学 / 科研"},
    "embodied": {"en": "Embodied / robotics", "zh": "具身 / 机器人"},
    "conversation": {"en": "Dialogue", "zh": "对话"},
    "multimodal": {"en": "Multimodal", "zh": "多模态"},
    "other": {"en": "General", "zh": "综合 / 其他"},
}

THEME_LABELS = {
    "web": {"en": "Web agents", "zh": "网页智能体"},
    "gui": {"en": "GUI agents", "zh": "GUI 智能体"},
    "coding": {"en": "Coding agents", "zh": "代码智能体"},
    "tool-use": {"en": "Tool use", "zh": "工具使用"},
    "multi-agent": {"en": "Multi-agent", "zh": "多智能体"},
    "computer-use": {"en": "Computer use", "zh": "计算机使用"},
    "embodied": {"en": "Embodied / robotics", "zh": "具身 / 机器人"},
    "safety": {"en": "Safety", "zh": "安全"},
    "memory": {"en": "Memory", "zh": "记忆"},
    "planning": {"en": "Planning / reasoning", "zh": "规划 / 推理"},
    "research": {"en": "Research agents", "zh": "科研智能体"},
    "conversation": {"en": "Dialogue / customer", "zh": "对话 / 客服"},
    "multimodal": {"en": "Multimodal", "zh": "多模态"},
    "mobile": {"en": "Mobile agents", "zh": "移动智能体"},
    "science": {"en": "Science lab", "zh": "科学实验"},
    "rsi": {"en": "RSI / AI4AI", "zh": "RSI / AI4AI"},
    "workplace": {"en": "Work / office", "zh": "职场 / 办公"},
}
