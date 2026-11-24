import os, json, time, urllib.request, urllib.error
from datetime import datetime, timezone

KEY = os.environ.get("GEMINI_API_KEY")
WEBHOOK = os.environ.get("DISCORD_WEBHOOK_URL")
if not KEY or not WEBHOOK:
    raise SystemExit("Missing GEMINI_API_KEY or DISCORD_WEBHOOK_URL secret.")

MODELS = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-2.0-flash"]

now = datetime.now(timezone.utc)
today = now.strftime("%A %d %B %Y")

PROMPT = f"""You help Hands of Love Foundation, a children's charity in Uganda, with TikTok content.
Today is {today}. Write fresh content for today for an international audience
(USA, UK, Canada, Europe, Australia) who might become genuine donors.

Give exactly this, in plain text, short and clear:
1. THREE caption ideas (each under 150 characters, warm, honest, no pressure, no guilt-tripping).
2. TEN hashtags mixing charity, Uganda and general reach.
3. TWO video ideas that can be filmed on a phone in under 30 seconds.
4. ONE donor-trust tip (for example transparency about where money goes).

Rules: never invent statistics, trends or numbers. Never mention a specific child's name or
identifying details. Remind to only film children with guardian consent and to avoid pity-based imagery.
Do not claim anything is trending."""

def call(model):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = json.dumps({"contents": [{"parts": [{"text": PROMPT}]}]}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "Content-Type": "application/json", "x-goog-api-key": KEY})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    return data["candidates"][0]["content"]["parts"][0]["text"]

def send(text):
    data = json.dumps({"content": text[:1990]}).encode()
    req = urllib.request.Request(WEBHOOK, data=data, headers={
        "Content-Type": "application/json", "User-Agent": "HOL-Trend-Bot/1.0"})
    urllib.request.urlopen(req, timeout=30)
    time.sleep(1.3)

text, used = None, None
for m in MODELS:
    try:
        text = call(m)
        used = m
        break
    except Exception as e:
        print(f"{m} failed: {e}")

if not text:
    send("✍️ **AI caption ideas**\nNo data today (the Gemini request failed). Check the Actions log.")
    raise SystemExit("All models failed")

send(f"✍️ **AI Caption Ideas for Hands of Love**\n"
     f"Written by AI ({used}) on {today}. These are suggestions, not TikTok trend data.")

chunk = ""
for para in text.split("\n"):
    if len(chunk) + len(para) + 1 > 1800:
        send(chunk)
        chunk = ""
    chunk += para + "\n"
if chunk.strip():
    send(chunk)
print("Done")
