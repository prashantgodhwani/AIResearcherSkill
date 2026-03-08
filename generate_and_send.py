"""
AI Trends Newsletter Generator
Reads the skill definition from skill/SKILL.md as the source of truth,
then calls the Anthropic API to research and generate this week's AI trends,
and sends it as a formatted HTML newsletter via Gmail.

To update the newsletter behaviour, edit skill/SKILL.md — no need to touch this file.
"""

import os
import smtplib
import json
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
import anthropic

# ── Configuration ──────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY   = os.environ["ANTHROPIC_API_KEY"]
GMAIL_ADDRESS       = os.environ["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD  = os.environ["GMAIL_APP_PASSWORD"]
RECIPIENT_EMAIL     = os.environ["RECIPIENT_EMAIL"]

TODAY = datetime.now().strftime("%B %d, %Y")
WEEK  = datetime.now().strftime("Week of %B %d, %Y")

# ── Load Skill Definition ──────────────────────────────────────────────────────

def load_skill() -> str:
    """Read SKILL.md and extract the body (everything after the YAML frontmatter)."""
    skill_path = Path(__file__).parent.parent / "SKILL.md"
    content = skill_path.read_text(encoding="utf-8")

    # Strip YAML frontmatter (between --- markers)
    if content.startswith("---"):
        end = content.index("---", 3)
        content = content[end + 3:].strip()

    return content

# ── Prompts ────────────────────────────────────────────────────────────────────

def build_system_prompt(skill_body: str) -> str:
    return f"""You are an expert AI research assistant that produces weekly developer-focused
AI trend briefings. You have deep knowledge of LLMs, AI infrastructure, developer tooling,
open-source AI, and the broader AI industry landscape.

Below is your full skill definition — follow it precisely when producing the report,
including the Stat Filtering Rule, Learning Path format, section structure, and quality checklist.

─────────────────────────────────────────
{skill_body}
─────────────────────────────────────────

OUTPUT FORMAT REQUIREMENT:
Respond ONLY with a valid JSON object. No preamble, no explanation, no markdown fences.
The JSON must match the schema specified in the user message exactly."""


def build_user_prompt() -> str:
    return f"""Today is {TODAY}. Research and produce the weekly AI trends newsletter for {WEEK}.

Return a JSON object with this exact schema:

{{
  "week": "{WEEK}",
  "generated_on": "{TODAY}",
  "executive_summary": "3-5 sentence overview of the week's most important developments",
  "sections": [
    {{
      "title": "Section title (e.g. New Models & Capabilities)",
      "summary": "2-3 sentence intro to this section's theme",
      "items": [
        {{
          "headline": "Short headline for this item",
          "detail": "2-4 sentences of concrete detail — specs, what changed, what it does",
          "developer_note": "1-2 sentences on why this matters for someone building with AI",
          "learning_path": {{
            "topic": "Topic name",
            "total_time": "e.g. ~2 hrs",
            "steps": [
              {{
                "step": "Understand it",
                "time": "~20 min",
                "action": "What to read or watch",
                "resource": "Specific URL",
                "goal": "What you will understand after this"
              }},
              {{
                "step": "Try it",
                "time": "~45 min",
                "action": "Specific hands-on exercise",
                "resource": "Repo URL, playground, or exact CLI command",
                "goal": "What you will be able to do after this"
              }},
              {{
                "step": "Build with it",
                "time": "~1 hr",
                "action": "Small project idea",
                "resource": "Starter repo or template URL if available",
                "goal": "What this project teaches you"
              }}
            ]
          }}
        }}
      ]
    }}
  ],
  "learning_agenda": [
    {{
      "rank": 1,
      "topic": "Topic name",
      "why_now": "1 sentence on why this is the highest ROI skill to learn this week",
      "total_time": "~X hrs",
      "first_step": "Exactly what to do first, with a URL or command"
    }}
  ],
  "what_to_watch": [
    {{
      "item": "Thing to watch",
      "why": "1 sentence explanation",
      "timeline": "e.g. Next 2 weeks / Q2 2026"
    }}
  ]
}}

Follow the skill definition precisely:
- Apply the Stat Filtering Rule to every statistic
- Include Learning Paths (3 steps + time estimates) for the 2-3 most impactful items per section
- Populate learning_agenda with the top 4-5 Learning Paths ranked by developer ROI
- Cover sections: Headline Developments, New Models & Capabilities, Developer Tools & Frameworks,
  Open Source & Community, Infrastructure & Deployment
- 3-5 items per section
- learning_path is optional per item — only include it for significant topics"""

# ── Claude API Call ────────────────────────────────────────────────────────────

def generate_newsletter(skill_body: str) -> dict:
    print(f"Generating newsletter for {WEEK}...")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        system=build_system_prompt(skill_body),
        messages=[{"role": "user", "content": build_user_prompt()}]
    )

    raw = message.content[0].text.strip()

    # Strip markdown fences if model adds them despite instructions
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    return json.loads(raw)

# ── HTML Email Renderer ────────────────────────────────────────────────────────

def render_html(data: dict) -> str:
    sections_html = ""

    for section in data.get("sections", []):
        items_html = ""
        for item in section.get("items", []):
            lp = item.get("learning_path")
            lp_html = ""
            if lp:
                steps_html = ""
                for s in lp.get("steps", []):
                    resource = s.get("resource", "")
                    if resource.startswith("http"):
                        resource_html = f'<a href="{resource}" style="color:#2E7D32;">{resource}</a>'
                    else:
                        resource_html = f'<code style="background:#f5f5f5;padding:2px 6px;border-radius:3px;font-size:12px;">{resource}</code>'

                    steps_html += f"""
                    <tr>
                      <td style="padding:8px 12px;border-bottom:1px solid #e8f5e9;vertical-align:top;width:90px;">
                        <span style="font-weight:600;color:#2E7D32;font-size:12px;">{s.get('step','')}</span><br>
                        <span style="color:#888;font-size:11px;">{s.get('time','')}</span>
                      </td>
                      <td style="padding:8px 12px;border-bottom:1px solid #e8f5e9;font-size:13px;color:#333;">
                        {s.get('action','')} → {resource_html}<br>
                        <span style="color:#666;font-style:italic;">{s.get('goal','')}</span>
                      </td>
                    </tr>"""

                lp_html = f"""
                <div style="background:#f1f8e9;border-left:4px solid #2E7D32;border-radius:0 6px 6px 0;
                            margin:12px 0;padding:14px 16px;">
                  <div style="font-weight:700;color:#2E7D32;font-size:13px;margin-bottom:2px;">
                    🎯 Learning Path: {lp.get('topic','')}
                  </div>
                  <div style="color:#666;font-size:12px;margin-bottom:10px;">
                    ⏱ Total time: {lp.get('total_time','')}
                  </div>
                  <table style="width:100%;border-collapse:collapse;">
                    {steps_html}
                  </table>
                </div>"""

            items_html += f"""
            <div style="margin-bottom:24px;padding-bottom:24px;border-bottom:1px solid #f0f0f0;">
              <h3 style="margin:0 0 6px 0;font-size:15px;color:#1a1a1a;">{item.get('headline','')}</h3>
              <p style="margin:0 0 10px 0;font-size:14px;color:#444;line-height:1.6;">{item.get('detail','')}</p>
              <div style="background:#e8f0fe;border-left:4px solid #1F4E79;border-radius:0 6px 6px 0;
                          padding:10px 14px;margin-bottom:10px;">
                <span style="font-weight:700;color:#1F4E79;font-size:12px;">DEV NOTE </span>
                <span style="font-size:13px;color:#333;font-style:italic;">{item.get('developer_note','')}</span>
              </div>
              {lp_html}
            </div>"""

        sections_html += f"""
        <div style="margin-bottom:36px;">
          <h2 style="margin:0 0 6px 0;font-size:18px;color:#1F4E79;border-bottom:2px solid #2E75B6;
                     padding-bottom:8px;">{section.get('title','')}</h2>
          <p style="margin:0 0 18px 0;font-size:14px;color:#555;line-height:1.6;">{section.get('summary','')}</p>
          {items_html}
        </div>"""

    # Learning Agenda
    agenda_rows = ""
    for item in data.get("learning_agenda", []):
        first = item.get("first_step", "")
        first_html = f'<a href="{first}" style="color:#2E7D32;">{first}</a>' if first.startswith("http") else first
        agenda_rows += f"""
        <tr style="background:{'#fafafa' if item['rank'] % 2 == 0 else '#fff'};">
          <td style="padding:10px 12px;font-weight:700;color:#2E7D32;font-size:14px;width:30px;">#{item.get('rank','')}</td>
          <td style="padding:10px 12px;">
            <div style="font-weight:600;font-size:14px;color:#1a1a1a;">{item.get('topic','')}</div>
            <div style="font-size:12px;color:#666;margin-top:2px;">{item.get('why_now','')}</div>
          </td>
          <td style="padding:10px 12px;font-size:12px;color:#888;white-space:nowrap;">{item.get('total_time','')}</td>
          <td style="padding:10px 12px;font-size:12px;color:#444;">{first_html}</td>
        </tr>"""

    # What to Watch
    watch_html = ""
    for w in data.get("what_to_watch", []):
        watch_html += f"""
        <div style="display:flex;gap:12px;margin-bottom:12px;align-items:flex-start;">
          <span style="background:#fff3e0;color:#e65100;font-size:11px;font-weight:700;
                       padding:2px 8px;border-radius:12px;white-space:nowrap;margin-top:2px;">
            {w.get('timeline','')}
          </span>
          <div>
            <span style="font-weight:600;font-size:14px;color:#1a1a1a;">{w.get('item','')}</span>
            <span style="font-size:13px;color:#555;"> — {w.get('why','')}</span>
          </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f4f6f9;font-family:Arial,Helvetica,sans-serif;">

  <div style="background:linear-gradient(135deg,#1F4E79 0%,#2E75B6 100%);padding:32px 40px;">
    <div style="font-size:11px;color:#90CAF9;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px;">
      Weekly Developer Briefing
    </div>
    <h1 style="margin:0;font-size:28px;color:#fff;font-weight:700;">AI & Tech Trends</h1>
    <div style="font-size:14px;color:#90CAF9;margin-top:6px;">{data.get('week','')} · Prepared by Claude</div>
  </div>

  <div style="max-width:680px;margin:0 auto;padding:32px 24px;">

    <div style="background:#fff;border-radius:8px;padding:24px;margin-bottom:28px;
                box-shadow:0 1px 4px rgba(0,0,0,0.08);">
      <h2 style="margin:0 0 12px 0;font-size:16px;color:#1F4E79;">Executive Summary</h2>
      <p style="margin:0;font-size:14px;color:#444;line-height:1.7;">{data.get('executive_summary','')}</p>
    </div>

    <div style="background:#fff;border-radius:8px;padding:28px;margin-bottom:28px;
                box-shadow:0 1px 4px rgba(0,0,0,0.08);">
      {sections_html}
    </div>

    <div style="background:#fff;border-radius:8px;padding:28px;margin-bottom:28px;
                box-shadow:0 1px 4px rgba(0,0,0,0.08);">
      <h2 style="margin:0 0 6px 0;font-size:18px;color:#1F4E79;border-bottom:2px solid #2E75B6;padding-bottom:8px;">
        🗓 This Week's Learning Agenda
      </h2>
      <p style="margin:0 0 16px 0;font-size:13px;color:#666;">Ranked by developer ROI — start at #1 if you only have a few hours.</p>
      <table style="width:100%;border-collapse:collapse;font-size:13px;">
        <thead>
          <tr style="background:#f5f9ff;">
            <th style="padding:8px 12px;text-align:left;color:#1F4E79;font-size:12px;">#</th>
            <th style="padding:8px 12px;text-align:left;color:#1F4E79;font-size:12px;">Topic</th>
            <th style="padding:8px 12px;text-align:left;color:#1F4E79;font-size:12px;">Time</th>
            <th style="padding:8px 12px;text-align:left;color:#1F4E79;font-size:12px;">Start here</th>
          </tr>
        </thead>
        <tbody>{agenda_rows}</tbody>
      </table>
    </div>

    <div style="background:#fff;border-radius:8px;padding:28px;margin-bottom:28px;
                box-shadow:0 1px 4px rgba(0,0,0,0.08);">
      <h2 style="margin:0 0 16px 0;font-size:18px;color:#1F4E79;border-bottom:2px solid #2E75B6;padding-bottom:8px;">
        👀 What to Watch
      </h2>
      {watch_html}
    </div>

    <div style="text-align:center;padding:16px;font-size:12px;color:#999;">
      Generated by Claude · {TODAY} · You're receiving this because you set it up 🤖
    </div>

  </div>
</body>
</html>"""

# ── Send Email ─────────────────────────────────────────────────────────────────

def send_email(html: str, week: str):
    print(f"Sending newsletter to {RECIPIENT_EMAIL}...")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🤖 AI Trends — {week}"
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = RECIPIENT_EMAIL
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())

    print("Newsletter sent successfully!")

# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    skill_body = load_skill()
    print(f"Loaded skill definition ({len(skill_body)} chars)")

    data = generate_newsletter(skill_body)

    html = render_html(data)
    with open("newsletter_preview.html", "w") as f:
        f.write(html)
    print("Preview saved to newsletter_preview.html")

    send_email(html, data.get("week", WEEK))
