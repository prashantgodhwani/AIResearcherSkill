# AI Trends Newsletter — GitHub Actions Setup

Automatically generates and emails a weekly AI developer trends newsletter every Friday, powered by Claude.

---

## How it works

1. GitHub Actions triggers every Friday at 4PM UTC
2. A Python script calls the Claude API with a structured research prompt
3. Claude returns a JSON report covering this week's AI trends, learning paths, and what to watch
4. The script renders it as a polished HTML newsletter
5. It lands in your inbox via Gmail

---

## Setup (one-time, ~10 minutes)

### Step 1 — Fork or create the repo

Push this project to a GitHub repository (can be private).

### Step 2 — Get a Gmail App Password

Gmail requires an App Password (not your regular password) for SMTP access.

1. Go to your Google Account → **Security**
2. Make sure **2-Step Verification** is enabled
3. Go to **Security → 2-Step Verification → App passwords**
4. Create a new app password — name it "AI Newsletter"
5. Copy the 16-character password shown (you won't see it again)

> If you don't see "App passwords", your account may have Advanced Protection enabled.
> In that case, use SendGrid instead (free tier supports 100 emails/day).

### Step 3 — Add GitHub Secrets

In your GitHub repo, go to **Settings → Secrets and variables → Actions → New repository secret**.

Add these four secrets:

| Secret name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key (from console.anthropic.com) |
| `GMAIL_ADDRESS` | Your Gmail address (e.g. you@gmail.com) |
| `GMAIL_APP_PASSWORD` | The 16-character app password from Step 2 |
| `RECIPIENT_EMAIL` | Where to send the newsletter (can be same as GMAIL_ADDRESS) |

### Step 4 — Test it manually

Go to **Actions → Weekly AI Trends Newsletter → Run workflow** to trigger it immediately and confirm the email arrives.

---

## Customisation

**Change the send time:**
Edit the cron schedule in `.github/workflows/weekly-newsletter.yml`:
```yaml
- cron: '0 16 * * 5'   # Friday 4PM UTC
- cron: '0 9 * * 1'    # Monday 9AM UTC
- cron: '0 17 * * 4'   # Thursday 5PM UTC
```
Use [crontab.guru](https://crontab.guru) to build your schedule.

**Change the model:**
Edit `MODEL` in `scripts/generate_and_send.py`. Default is `claude-sonnet-4-20250514`.

**Send to multiple recipients:**
Change `RECIPIENT_EMAIL` to a comma-separated list and update the `sendmail` call:
```python
recipients = RECIPIENT_EMAIL.split(",")
server.sendmail(GMAIL_ADDRESS, recipients, msg.as_string())
```

---

## Cost

One newsletter = one Claude API call (~4,000–6,000 output tokens).
At Sonnet pricing, each run costs approximately **$0.02–0.04**.
52 weeks/year ≈ **under $2/year**.

---

## Troubleshooting

**Email not arriving?**
- Check GitHub Actions logs under the Actions tab
- Verify all 4 secrets are set correctly
- Make sure your Gmail App Password is correct (no spaces)
- Check your spam folder

**Claude API error?**
- Verify your `ANTHROPIC_API_KEY` is valid at console.anthropic.com
- Check you have sufficient API credits
