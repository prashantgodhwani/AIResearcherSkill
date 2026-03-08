---
name: ai-trends-researcher
description: >
  Use this skill whenever the user wants to research, discover, or stay updated on AI and tech trends,
  news, tools, frameworks, or breakthroughs. Trigger this skill when the user asks things like:
  "what's new in AI", "summarize recent AI trends", "research the latest in LLMs", "what AI tools
  should I know about", "generate a report on AI news", "what's happening in machine learning",
  "give me a developer briefing on AI", or any variation of wanting a structured overview of
  the current AI/tech landscape. Always use this skill even if the request is casual — e.g.,
  "catch me up on AI" or "what's trending in tech" — as long as it touches on AI or developer tools.
  Output is always a polished Word (.docx) report unless the user explicitly asks for something else.
---

# AI Trends Researcher

A skill for searching, synthesizing, and delivering structured AI & tech trend reports as professional Word documents.

---

## Goal

Produce a well-researched, developer-focused briefing on current AI/tech trends. The report should feel like something a senior engineer would write after a focused research session — concrete, insightful, and actionable.

---

## Workflow

### Step 1: Clarify Scope (if needed)

If the user's request is very broad (e.g. "AI trends"), briefly confirm:
- **Topic focus**: General AI landscape? A specific domain (LLMs, agents, infra, open-source, a specific company)?
- **Time range**: Last week? Last month? Last quarter? (Default: last 30 days)
- **Audience**: Developer? Executive? General? (Default: developer / technical)

If the request is specific enough, skip straight to research.

---

### Step 2: Web Research

Run **5–8 targeted web searches** to gather breadth and depth. Suggested queries:

```
AI news [current month year]
latest LLM model releases [year]
AI developer tools trends [year]
open source AI frameworks [year]
AI agents breakthroughs [year]
AI infrastructure updates [year]
[specific topic from user] latest developments
```

For each major finding, use `web_fetch` to retrieve the full article if the snippet is too brief.

**Research targets to cover (adapt to topic):**
- New model releases or updates (OpenAI, Anthropic, Google, Meta, Mistral, etc.)
- Developer tooling & frameworks (LangChain, LlamaIndex, CrewAI, smolagents, etc.)
- Infrastructure & deployment (inference, fine-tuning, hardware)
- Open-source highlights (Hugging Face, GitHub trending)
- Industry moves (funding, acquisitions, partnerships)
- Emerging techniques (RAG updates, agent patterns, evals, multimodal, etc.)

---

### Step 3: Synthesize

Organize findings into **4–6 thematic sections**. Each section should:
- Lead with a 2–3 sentence summary of the trend
- Call out 2–4 specific examples, tools, or news items
- Include a **"Developer Note"** — why it matters for someone building with AI
- Include a **"Learning Path"** box (see format below) for every major topic

**Learning Path box format** (include for every significant topic/tool/model):

```
Learning Path: [Topic Name]
Total time: ~X hours

Step 1 - Understand it (~X min)
  Read/Watch: [specific doc, video, or article with URL]
  Goal: [what you'll understand after this]

Step 2 - Try it (~X min / X hrs)
  Do: [specific hands-on exercise — run a script, call an API, clone a repo]
  Starter: [repo URL, playground link, or exact command]

Step 3 - Build with it (~X hrs)
  Project: [a small but real project that cements the skill]
  Why: [what this project teaches you]
```

Guidelines for Learning Paths:
- **Be specific**: name the exact doc page, video, or GitHub repo — not just "read the docs"
- **Be realistic with time estimates**: a 30-page paper is not a 15-min read
- **Prioritize hands-on**: every path must have at least one "try it" step
- **Match difficulty to the topic**: a new model API call is ~1hr; a new agent framework is ~4hrs
- **Use real URLs** from your web research where possible
- Focus on the 2–3 most impactful topics per section — not every bullet needs a path

Suggested section structure (adapt as needed):
1. **Headline Developments** — the biggest news items
2. **New Models & Capabilities** — notable releases and benchmarks
3. **Developer Tools & Frameworks** — what's shipping, what's gaining traction
4. **Open Source & Community** — notable repos, releases, community momentum
5. **Infrastructure & Deployment** — compute, serving, fine-tuning
6. **This Week's Learning Agenda** — consolidated top 3–5 Learning Paths from the whole report, ranked by "highest ROI for a developer right now"
7. **What to Watch** — emerging trends, upcoming releases, things to keep an eye on

---

### Step 4: Generate the Word Document

Use `docx-js` to produce a professional `.docx` report. Follow the docx skill (`/mnt/skills/public/docx/SKILL.md`) for all formatting rules.

**Document structure:**

```
[Cover area]
  Title: "AI & Tech Trends Briefing"
  Subtitle: [Topic or "Weekly/Monthly Developer Briefing"]
  Date: [Today's date]
  Prepared by: Claude

[Executive Summary] — 3–5 sentence high-level overview

[Thematic Sections] — as outlined above, each containing:
  - News/analysis bullets
  - Developer Note callout (left blue border, italic)
  - Learning Path box(es) (shaded box, green left border) for major topics

[This Week's Learning Agenda] — consolidated top Learning Paths ranked by dev ROI

[What to Watch]

[Sources] — bulleted list of URLs used in research
```

**Learning Path box styling in the Word doc:**
- Render as a shaded box with a green (`2E7D32`) left border, 12pt thick
- Header line: bold, e.g. "Learning Path: Getting Started with DeepSeek V4"
- Sub-header: "Total time: ~2 hrs" in italic gray
- Steps formatted as numbered items inside the box
- Use a light green shading (`F1F8E9`) for the box background
- Separate each Learning Path from surrounding content with a spacer paragraph

**Formatting guidelines:**
- US Letter, 1" margins
- Font: Arial, 12pt body
- Heading 1 for major sections, Heading 2 for subsections
- Use proper bullet lists (LevelFormat.BULLET — never unicode bullets)
- Use a simple summary table at the top if there are 4+ distinct topics covered:

| Topic | Key Takeaway | Relevance |
|-------|-------------|-----------|
| ...   | ...         | ...       |

- Keep the tone: **informative, technical, concise** — no fluff

**Validation:**
After generating, run:
```bash
python scripts/office/validate.py report.docx
```
Fix any issues before presenting the file.

---

### Step 5: Deliver

- Save final file to `/mnt/user-data/outputs/ai-trends-[date].docx`
- Use `present_files` to share with the user
- Provide a 2–3 sentence summary of the top highlights in chat

---

## Quality Checklist

Before delivering, confirm:
- [ ] At least 5 web searches were run
- [ ] Report covers at least 4 distinct themes
- [ ] Each section has concrete examples (named tools, models, companies)
- [ ] Every major topic has a Learning Path with realistic time estimates
- [ ] Every Learning Path has a specific "try it" step with a real URL or command
- [ ] "This Week's Learning Agenda" section is populated and ranked
- [ ] Sources section is populated
- [ ] Document validated without errors
- [ ] File saved to outputs and presented

---

## Tips

- **Recency matters**: Always include the current date in searches to get fresh results
- **Go beyond headlines**: Use `web_fetch` to get substance from articles, not just titles
- **Developer lens**: Frame everything around "what does this mean for someone building with AI?"
- **Avoid hype**: Skip vague claims; favor concrete releases, benchmarks, and code

## Stat Filtering Rule

Not all numbers are equal. Apply this filter to every statistic before including it:

**Keep — technical specs that describe what a technology *is* or *can do*:**
- Model size (e.g. "1 trillion parameters", "32B active params per token")
- Context window (e.g. "1M token context window")
- Benchmark scores (e.g. "77.1% on ARC-AGI-2", "94% on SWE-bench")
- Latency / cost per token (e.g. "$0.25/M input tokens")
- API limits, quantization specs, hardware requirements

**Drop — adoption/market stats that describe *how popular* something is:**
- Usage percentages (e.g. "75% of developers use X", "66% surge in TypeScript usage")
- Survey rankings (e.g. "#1 most-used tool", "overtook Copilot")
- GitHub star counts (e.g. "188,000 stars")
- Market share figures (e.g. "15% global AI market share")
- Download counts (e.g. "97M monthly SDK downloads")

For adoption trends, **state the signal without the number**: instead of "TypeScript surged 66% to become GitHub's #1 language driven by AI compatibility", write "TypeScript has become the most AI-compatible language choice for web and agent stacks — strongly-typed languages reduce LLM errors significantly."

The test: ask "does this number help me decide what to build or how to use the technology?" If yes, keep it. If it's just context on how popular something is, drop it.
