#!/usr/bin/env python3
"""Render feed.xml + index.html for the WestXDC stories feed (WPEmatico source).

Source of truth: stories.json beside this script. Only stories whose image
file exists on disk are included. Base URL comes from site_config.json
({"base_url": "https://OWNER.github.io/REPO"}) — no trailing slash.
"""
import json, os, sys
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

HERE = os.path.dirname(os.path.abspath(__file__))

def load(name, default=None):
    p = os.path.join(HERE, name)
    if not os.path.exists(p):
        return default
    with open(p) as f:
        return json.load(f)

def main():
    cfg = load("site_config.json", {})
    base = cfg.get("base_url", "https://example.github.io/westxdc-stories").rstrip("/")
    stories = load("stories.json", [])
    ready = [s for s in stories if os.path.exists(os.path.join(HERE, s["image"]))]
    skipped = [s["id"] for s in stories if s not in ready]
    ready.sort(key=lambda s: s["pubDate"], reverse=True)

    items = []
    lis = []
    for s in ready:
        dt = datetime.strptime(s["pubDate"], "%Y-%m-%d").replace(hour=14, tzinfo=timezone.utc)
        img_url = f"{base}/{s['image']}"
        body_html = f'<p><img src="{img_url}" alt="{escape(s["title"])}" /></p>' + "".join(
            f"<p>{escape(p)}</p>" for p in s["body"])
        items.append(f"""    <item>
      <title>{escape(s['title'])}</title>
      <link>{base}/index.html#{s['slug']}</link>
      <guid isPermaLink="false">{s['id']}</guid>
      <pubDate>{format_datetime(dt)}</pubDate>
      <category>{escape(s['current'])}</category>
      <description>{escape(s['summary'])}</description>
      <content:encoded><![CDATA[{body_html}]]></content:encoded>
      <media:content url="{img_url}" type="image/jpeg" medium="image" />
      <enclosure url="{img_url}" type="image/jpeg" length="0" />
    </item>""")
        lis.append(f'      <li><a href="feed.xml">{escape(s["title"])}</a> — {escape(s["summary"])}</li>')

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>WestXDC — Currents Stories</title>
    <link>https://westxdc.com</link>
    <description>Short stories from the WestXDC map of Northern Virginia's creative innovation economy — the unexpected connections between the region's technology, creativity, capital, and community.</description>
    <language>en-us</language>
    <atom:link href="{base}/feed.xml" rel="self" type="application/rss+xml" />
{chr(10).join(items)}
  </channel>
</rss>
"""
    with open(os.path.join(HERE, "feed.xml"), "w") as f:
        f.write(feed)

    index = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>WestXDC — Currents Stories feed</title></head>
<body>
<h1>WestXDC — Currents Stories</h1>
<p>Machine-readable story feed for WPEmatico: <a href="feed.xml">feed.xml</a></p>
<ul>
{chr(10).join(lis)}
</ul>
</body></html>
"""
    with open(os.path.join(HERE, "index.html"), "w") as f:
        f.write(index)
    open(os.path.join(HERE, ".nojekyll"), "a").close()

    print(f"feed items: {len(ready)}; skipped (no image yet): {skipped}")

if __name__ == "__main__":
    main()
