import os, json, time, urllib.request, urllib.error
from datetime import datetime, timezone

KEY = (os.environ.get("GEMINI_API_KEY") or "").strip()
WEBHOOK = (os.environ.get("DISCORD_WEBHOOK_URL") or "").strip()
if not KEY or not WEBHOOK:
    raise SystemExit("Missing GEMINI_API_KEY or DISCORD_WEBHOOK_URL secret.")

now = datetime.now(timezone.utc)
today = now.strftime("%A %d %B %Y")

PROMPT = f"""You help Hands of Love Foundation, a children's charity, grow on TikTok.
Today is {today}. The goal is to reach NEW supporters and genuine donors in the USA, UK,
Canada, Germany, France, Netherlands, Switzerland, Sweden, Norway, Denmark, Ireland,
Belgium and Australia. Write in English for that audience.

Give exactly this, in plain text, short and clear:
1. THREE caption ideas (each under 150 characters). Focus on universal feelings: kindness,
   hope, childhood, education, meals, giving back. Do not lead with the country name. Mention
   Africa or Uganda at most once across all captions, only where it feels natural.
2. TEN hashtags for broad GLOBAL reach on TikTok. Use general ones such as charity, giving,
   kindness, donate, nonprofit, makeadifference, wholesome, hope. Do NOT use Uganda-specific
   hashtags. Use at most one Africa hashtag.
3. TWO video ideas that can be filmed on a phone in under 30 seconds and would suit viewers in
   those countries (wholesome, uplifting, easy to share).
4. ONE donor-trust tip (for example showing where donations go).
5. ONE timing idea if a major giving season is near (such as GivingTuesday or Christmas).

Rules: never invent statistics, trends or numbers. Never claim a hashtag is trending today.
Never mention a specific child's name or identifying details. Only film children with
guardian consent. Avoid pity-based imagery and avoid language that makes supporters feel like
saviours; show children with dignity."""

def send(text):
    data = json.dumps({"content": text[:1990]}).encode()
    req = urllib.request.Request(WEBHOOK, data=data, headers={
        "Content-Type": "application/json", "User-Agent": "HOL-Trend-Bot/1.0"})
    urllib.request.urlopen(req, timeout=30)
    time.sleep(1.3)

def api(url, body=None):
    headers = {"Content-Type": "application/json", "x-goog-api-key": KEY}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def err_text(e):
    if isinstance(e, urllib.error.HTTPError):
        try:
            msg = json.load(e)["error"]["message"]
        except Exception:
            msg = ""
        return f"HTTP {e.code} {msg}"[:300]
    return str(e)[:300]

errors = []
models = []
try:
    listing = api("https://generativelanguage.googleapis.com/v1beta/models?pageSize=100")
    for m in listing.get("models", []):
        name = m["name"].replace("models/", "")
        if "generateContent" in m.get("supportedGenerationMethods", []) and "flash" in name \
           and not any(x in name for x in ("image", "tts", "live", "audio", "embedding", "thinking")):
            models.append(name)
    models.sort(key=lambda n: ("lite" in n, n), reverse=False)
except Exception as e:
    errors.append("List models: " + err_text(e))

if not models:
    models = ["gemini-2.5-flash", "gemini-flash-latest"]

text, used = None, None
for m in models[:4]:
    try:
        data = api(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
                   {"contents": [{"parts": [{"text": PROMPT}]}]})
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        used = m
        break
    except Exception as e:
        errors.append(f"{m}: " + err_text(e))

if not text:
    send("✍️ **AI caption ideas**\nNo data today. Gemini errors:\n" + "\n".join(errors))
    raise SystemExit("All models failed")

send(f"✍️ **AI Caption Ideas for Hands of Love**\n"
     f"Written by AI ({used}) on {today}. These are suggestions, not live TikTok trend data. "
     f"For real trending hashtags and sounds, use today's TikTok Creative Center links.")

chunk = ""
for para in text.split("\n"):
    if len(chunk) + len(para) + 1 > 1800:
        send(chunk)
        chunk = ""
    chunk += para + "\n"
if chunk.strip():
    send(chunk)
print("Done")
