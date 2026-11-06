import asyncio
import datetime as dt
import json
from pathlib import Path

import edge_tts

JST = dt.timezone(dt.timedelta(hours=9))
today = dt.datetime.now(JST).strftime("%Y-%m-%d")

news_file = Path("drafts") / f"{today}-news.json"
output_dir = Path("audio")
output_dir.mkdir(parents=True, exist_ok=True)

with news_file.open("r", encoding="utf-8") as f:
    data = json.load(f)

sections = [
    f"おはようございます。今日は{dt.datetime.now(JST).month}月"
    f"{dt.datetime.now(JST).day}日です。今日のニュースをお伝えします。"
]

for category, articles in data.get("categories", {}).items():
    if not articles:
        continue

    sections.append(f"続いて、{category}のニュースです。")

    for article in articles:
        title = article.get("title", "").strip()
        if title:
            sections.append(title)

sections.append("以上、今日のニュースでした。")

script = "\n".join(sections)
(output_dir / "news-script.txt").write_text(script, encoding="utf-8")


async def main():
    speech = edge_tts.Communicate(
        text=script,
        voice="ja-JP-NanamiNeural",
        rate="-5%"
    )
    await speech.save(str(output_dir / f"{today}-ja.mp3"))


asyncio.run(main())
