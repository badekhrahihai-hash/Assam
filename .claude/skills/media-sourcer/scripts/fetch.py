#!/usr/bin/env python3
"""media-sourcer: videos, clips, images, news articles. Usage: see SKILL.md"""
import argparse, os, re, subprocess, sys, shutil, urllib.request, urllib.parse
from pathlib import Path

def ensure(mod, pkg=None):
    try:
        __import__(mod)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg or mod])

def run(cmd):
    print("+", " ".join(cmd)); return subprocess.call(cmd)

def ytdlp(args):
    ensure("yt_dlp", "yt-dlp")
    return run([sys.executable, "-m", "yt_dlp", *args])

def video(a):
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tmpl = str(out / "%(title).80s [%(id)s].%(ext)s")
    if a.audio:
        return ytdlp(["-x", "--audio-format", "mp3", "-o", tmpl, a.url])
    fmt = "bv*+ba/b" if a.quality == "best" else f"bv*[height<={a.quality}]+ba/b[height<={a.quality}]"
    return ytdlp(["-f", fmt, "--merge-output-format", "mp4", "-o", tmpl, a.url])

def clip(a):
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    tmpl = str(out / "clip %(title).60s [%(id)s].%(ext)s")
    return ytdlp(["--download-sections", f"*{a.start}-{a.end}", "--force-keyframes-at-cuts",
                  "-f", "bv*[height<=1080]+ba/b", "--merge-output-format", "mp4", "-o", tmpl, a.url])

def images(a):
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    ensure("gallery_dl", "gallery-dl")
    rc = run([sys.executable, "-m", "gallery_dl", "-d", str(out), a.url])
    if rc != 0:  # fallback: plain <img> scrape
        return scrape_imgs(a.url, out)
    return 0

def scrape_imgs(url, out, limit=40):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    srcs = re.findall(r'(?:src|data-src|content)=["\']([^"\']+\.(?:jpg|jpeg|png|webp)[^"\']*)', html, re.I)
    seen, n = set(), 0
    for s in srcs:
        u = urllib.parse.urljoin(url, s)
        if u in seen: continue
        seen.add(u)
        name = re.sub(r"[^\w.\-]", "_", os.path.basename(urllib.parse.urlparse(u).path))[:80] or f"img{n}.jpg"
        try:
            urllib.request.urlretrieve(u, out / name); n += 1; print("saved", name)
        except Exception as e:
            print("skip", u, e)
        if n >= limit: break
    print(f"{n} images saved to {out}"); return 0 if n else 1

def article(a):
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    ensure("trafilatura")
    import trafilatura
    html = trafilatura.fetch_url(a.url)
    if not html:
        print("Could not fetch (blocked/paywalled?)"); return 1
    text = trafilatura.extract(html, output_format="markdown", include_images=True, with_metadata=True)
    if not text:
        print("No article text found"); return 1
    slug = re.sub(r"[^\w]+", "-", urllib.parse.urlparse(a.url).path.strip("/"))[-60:] or "article"
    (out / f"{slug}.md").write_text(f"Source: {a.url}\n\n{text}\n")
    print("saved", out / f"{slug}.md")
    scrape_imgs(a.url, out / f"{slug}_images", limit=15)
    return 0

def search(a):
    return ytdlp(["--flat-playlist", "--print", "%(title)s | %(duration_string)s | %(webpage_url)s",
                  f"ytsearch{a.n}:{a.query}"])

p = argparse.ArgumentParser(); sp = p.add_subparsers(dest="cmd", required=True)
def add(name, fn, *args):
    s = sp.add_parser(name); s.set_defaults(fn=fn)
    for x, kw in args: s.add_argument(x, **kw)
    s.add_argument("--out", default="downloads"); return s
add("video", video, ("url", {}), ("--quality", {"default": "best"}), ("--audio", {"action": "store_true"}))
add("clip", clip, ("url", {}), ("start", {}), ("end", {}))
add("images", images, ("url", {}))
add("article", article, ("url", {}))
add("search", search, ("query", {}), ("--n", {"type": int, "default": 5}))
a = p.parse_args(); sys.exit(a.fn(a))
