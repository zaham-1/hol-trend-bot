import os, json, urllib.request

url = os.environ.get("DISCORD_WEBHOOK_URL")
if not url:
    raise SystemExit("No webhook secret found.")

msg = {"content": "✅ Hands of Love Trend Bot is connected. Real trend alerts are coming next."}
req = urllib.request.Request(
    url,
    data=json.dumps(msg).encode(),
    headers={"Content-Type": "application/json", "User-Agent": "HOL-Trend-Bot/1.0"},
)
urllib.request.urlopen(req)
print("Message sent")
