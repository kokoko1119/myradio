#!/usr/bin/env python3
"""Fetch public RSS headlines and prepare a draft for Mono Radio.

This script does not overwrite existing episodes or audio files.
"""
import datetime as dt
import email.utils
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

CATEGORIES = {
    "AI・テクノロジー": "AI テクノロジー 最新",
    "国内・海外": "日本 世界 主要ニュース",
    "医療・介護": "医療 介護 厚生労働省",
    "釣り": "沼津 小田原 熱海 釣り 釣果",
    "ゲーム": "グランブルーファンタジー ゲーム",
}


def fetch(query, limit=3):
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({
        "q": query + " when:3d", "hl": "ja", "gl": "JP", "ceid": "JP:ja"
    })
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 MonoRadio/1.0"})
    with urllib.request.urlopen(req, timeout=20) as response:
        root = ET.fromstring(response.read())
    items = []
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        published = (item.findtext("pubDate") or "").strip()
        if not title or not link:
            continue
        items.append({"title": re.sub(r"\s+", " ", title), "url": link, "published": published})
        if len(items) >= limit:
            break
    return items


def main():
    now = dt.datetime.now(dt.timezone(dt.timedelta(hours=9)))
    result = {"date": now.date().isoformat(), "generated_at": now.isoformat(), "categories": {}}
    for category, query in CATEGORIES.items():
        try:
            result["categories"][category] = fetch(query)
            print(f"{category}: {len(result['categories'][category])} items")
        except Exception as exc:
            result["categories"][category] = []
            print(f"{category}: failed ({exc})")
    output = Path("drafts") / f"{result['date']}-news.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {output}")
    print("Note: Headlines are research leads, not verified broadcast scripts.")


if __name__ == "__main__":
    main()
  
