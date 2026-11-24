import os, json, re, time, urllib.request, urllib.parse
from datetime import datetime, timezone

API_KEY = os.environ.get("YOUTUBE_API_KEY")
WEBHOOK = os.environ.get("DISCORD_WEBHOOK_URL")
if not API_KEY or not WEBHOOK:
    raise SystemExit("Missing YOUTUBE_API_KEY or DISCORD_WEBHOOK_URL secret.")

COUNTRIES = {
    "US": "🇺🇸 United States", "GB": "🇬🇧 United Kingdom", "CA": "🇨🇦 Canada",
    "DE": "🇩🇪 Germany", "FR": "🇫🇷 France", "NL": "🇳🇱 Netherlands",
    "CH": "🇨🇭 Switzerland", "SE": "🇸🇪 Sweden", "NO": "🇳🇴 Norway",
    "DK": "🇩🇰 Denmark", "IE": "🇮🇪 Ireland", "BE": "🇧🇪 Belgium",
    "AU": "🇦🇺 Australia",
}

# Basic safety filter for a children's charity (keyword based, not perfect)
BLOCK = ["war", "kill", "killed", "murder", "dead", "death", "shooting", "gun",
         "porn", "sex", "nsfw", "drunk", "vape", "gore", "suicide", "terror"]
BLOCK_RE = re.compile(r"\b(" + "|".join(BLOCK) + r")\b", re.I)

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "HOL-Trend-Bot/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

def seconds(iso):
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 99999
    h, mi, s = [int(x or 0) for x in m.groups()]
    return h * 3600 + mi * 60 + s

def fetch(region):
    params = urllib.parse.urlencode({
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular", "regionCode": region,
        "maxResults": 50, "key": API_KEY,
    })
    return get_json("https://www.googleapis.com/youtube/v3/videos?" + params)["items"]

def fmt(n):
    n = int(n)
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000: return f"{n/1_000:.1f}K"
    return str(n)

def send(text):
    data = json.dumps({"content": text[:1990]}).encode()
    req = urllib.request.Request(WEBHOOK, data=data, headers={
        "Content-Type": "application/json", "User-Agent": "HOL-Trend-Bot/1.0"})
    urllib.request.urlopen(req, timeout=30)
    time.sleep(1.3)

now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
send(f"📊 **Hands of Love Trend Report**\nSource: YouTube Data API (official, live)\nGenerated: {now}\n"
     f"Shows Shorts-length videos (60s or less) found in each country's top 50 trending list.")

for code, name in COUNTRIES.items():
    try:
        items = fetch(code)
        shorts = []
        for v in items:
            if seconds(v["contentDetails"]["duration"]) > 60:
                continue
            title = v["snippet"]["title"]
            desc = v["snippet"].get("description", "")
            if BLOCK_RE.search(title + " " + desc[:300]):
                continue
            tags = list(dict.fromkeys(re.findall(r"#\w+", title + " " + desc)))[:5]
            views = v.get("statistics", {}).get("viewCount", 0)
            shorts.append((title[:80], views, v["id"], tags))
        lines = [f"**{name}**"]
        if not shorts:
            lines.append("No Shorts-length videos in today's top 50 trending list.")
        for i, (t, views, vid, tags) in enumerate(shorts[:3], 1):
            lines.append(f"{i}. {t} ({fmt(views)} views)")
            lines.append(f"<https://www.youtube.com/shorts/{vid}>")
            if tags:
                lines.append("Hashtags: " + " ".join(tags))
        send("\n".join(lines))
    except Exception as e:
        print(f"{code} failed: {e}")
        send(f"**{name}**\nNo data (YouTube request failed).")

print("Done")
