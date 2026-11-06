---
name: media-sourcer
description: Download videos, audio, images, and news articles (text + images) from URLs on the internet. Use when the user wants to grab, save, download, clip, or source media from YouTube, Twitter/X, TikTok, Vimeo, Instagram, Reddit, Pinterest, news sites, or any web page. Also supports searching YouTube and trimming video clips.
---

# Media Sourcer

One script, no extra reasoning needed. Run it, report the output folder.

Script: `scripts/fetch.py` (auto-installs yt-dlp, gallery-dl, trafilatura on first use).

## Commands
```bash
python3 scripts/fetch.py video   URL [--quality 720] [--audio] [--out DIR]
python3 scripts/fetch.py clip    URL START END [--out DIR]      # e.g. 00:01:10 00:01:40
python3 scripts/fetch.py images  URL [--out DIR]                # gallery/social/page images
python3 scripts/fetch.py article URL [--out DIR]                # news clipping: text .md + images
python3 scripts/fetch.py search  "query" [--n 5]                # YouTube search, prints URLs
```
Default output: `./downloads/`. Quality: best, 1080, 720, 480, 360.

## Workflow
1. Pick command from the URL/intent (video site -> `video`/`clip`; news/blog -> `article`; image gallery or social post -> `images`).
2. Run it, then list the output folder for the user.
3. If a source fails (login/geo/paywall), say so briefly; do not bypass paywalls or DRM.

## Rules
- Only download content the user has rights to use or that is freely licensed; remind once for news/stock/footage reuse.
- Never download from paywalled/DRM sources by circumvention.
- Keep replies short: file paths + sizes.
