import os, json, time, urllib.request
from datetime import datetime, timezone

WEBHOOK = os.environ.get("DISCORD_WEBHOOK_URL")
if not WEBHOOK:
    raise SystemExit("Missing DISCORD_WEBHOOK_URL secret.")

COUNTRIES = [
    ("US", "🇺🇸 United States"), ("GB", "🇬🇧 United Kingdom"), ("CA", "🇨🇦 Canada"),
    ("DE", "🇩🇪 Germany"), ("FR", "🇫🇷 France"), ("NL", "🇳🇱 Netherlands"),
    ("CH", "🇨🇭 Switzerland"), ("SE", "🇸🇪 Sweden"), ("NO", "🇳🇴 Norway"),
    ("DK", "🇩🇰 Denmark"), ("IE", "🇮🇪 Ireland"), ("BE", "🇧🇪 Belgium"),
    ("AU", "🇦🇺 Australia"),
]

BASE = "https://ads.tiktok.com/business/creativecenter/inspiration/popular"

def link(kind, code):
    return f"{BASE}/{kind}/pc/en?countryCode={code}&period=7"

CAPTIONS = [
    "One small gift can change a child's whole week. Meet the kids of Hands of Love in Uganda. 💛 #HandsOfLove #Uganda #Charity",
    "A day in the life at Hands of Love. Every smile here is made possible by people like you. #HandsOfLove #Uganda #GiveHope",
    "Watch what a single meal means to a child in Uganda. Link in bio to help. #HandsOfLove #Uganda #Donate",
    "Behind the scenes with our team in Uganda. Real kids, real change. #HandsOfLove #CharityTok #Uganda",
    "Your kindness reaches further than you think. See where it lands. #HandsOfLove #Uganda #MakeADifference",
    "Meet the children you're helping. Their stories deserve to be heard. #HandsOfLove #Uganda #KidsCharity",
    "Small acts, big hearts. This is Hands of Love. #HandsOfLove #Uganda #Kindness",
]

def send(text):
    data = json.dumps({"content": text}).encode()
    req = urllib.request.Request(WEBHOOK, data=data, headers={
        "Content-Type": "application/json", "User-Agent": "HOL-Trend-Bot/1.0"})
    urllib.request.urlopen(req, timeout=30)
    time.sleep(1.3)

now = datetime.now(timezone.utc)
stamp = now.strftime("%Y-%m-%d %H:%M UTC")

send(f"🎵 **Hands of Love TikTok Trend Links**\nGenerated: {stamp}\n"
     "Source: TikTok Creative Center (TikTok's own public trend pages, last 7 days).\n"
     "⚠️ These are links to live TikTok pages. The bot does not read the numbers yet.")

chunk = ""
for code, name in COUNTRIES:
    line = (f"**{name}**\n"
            f"#️⃣ [Hashtags](<{link('hashtag', code)}>) | "
            f"🎵 [Sounds](<{link('music', code)}>) | "
            f"🎬 [Videos](<{link('video', code)}>)\n")
    if len(chunk) + len(line) > 1800:
        send(chunk)
        chunk = ""
    chunk += line
if chunk:
    send(chunk)

idea = CAPTIONS[now.timetuple().tm_yday % len(CAPTIONS)]
send("✍️ **Caption idea for today** (my suggestion, not TikTok data)\n" + idea +
     "\n\n🎬 **How to use it:** open a country's Sounds link, pick a sound that fits a "
     "children's charity (avoid anything violent or adult), and post a short real clip from "
     "your work with that sound.")
print("Done")
