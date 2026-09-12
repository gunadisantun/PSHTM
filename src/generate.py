from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import feedparser
import requests
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
TZ = ZoneInfo(CONFIG.get("timezone", "Asia/Jakarta"))
UA = "PSHTM-Daily-Instagram-Agent/2.0"


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", text.lower())).strip()


def entry_datetime(entry: Any) -> datetime:
    st = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    return datetime(*st[:6], tzinfo=timezone.utc) if st else datetime.now(timezone.utc)


def source_from_entry(entry: Any, title: str) -> str:
    source = getattr(entry, "source", None)
    if isinstance(source, dict) and source.get("title"):
        return source["title"].strip()
    return title.rsplit(" - ", 1)[-1].strip() if " - " in title else "Sumber berita"


def fetch_candidates() -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc)
    max_age = timedelta(hours=int(CONFIG.get("max_age_hours", 36)))
    out = []
    for feed_url in CONFIG["feeds"]:
        try:
            resp = requests.get(feed_url, headers={"User-Agent": UA}, timeout=20)
            resp.raise_for_status()
            feed = feedparser.parse(resp.content)
        except Exception as exc:
            print(f"Feed gagal: {exc}")
            continue
        for entry in feed.entries:
            raw = str(getattr(entry, "title", "")).strip()
            link = str(getattr(entry, "link", "")).strip()
            if not raw or not link:
                continue
            published = entry_datetime(entry)
            if now - published > max_age:
                continue
            source = source_from_entry(entry, raw)
            suffix = f" - {source}"
            title = raw[:-len(suffix)].strip() if raw.endswith(suffix) else raw
            out.append({"title": title, "source": source, "link": link, "published_utc": published.isoformat()})
    return out


def load_history(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def duplicate(title: str, history: list[dict[str, Any]]) -> bool:
    a = norm(title)
    for item in history:
        b = norm(str(item.get("title", "")))
        if b and (a == b or SequenceMatcher(None, a, b).ratio() >= 0.87):
            return True
    return False


def score(item: dict[str, Any]) -> float:
    text = norm(item["title"])
    value = sum(float(w) for k, w in CONFIG["keywords"].items() if norm(k) in text)
    published = datetime.fromisoformat(item["published_utc"])
    age_hours = max(0.0, (datetime.now(timezone.utc) - published).total_seconds() / 3600)
    return value + max(0.0, 12.0 - age_hours / 3.0)


def impact_line(title: str) -> str:
    t = norm(title)
    if any(x in t for x in ("breach", "kebocoran", "ransomware", "cyberattack")):
        return "Relevan untuk respons insiden, keamanan informasi, dan kewajiban pemberitahuan jika data pribadi terdampak."
    if any(x in t for x in ("privacy", "data protection", "personal data", "data pribadi", "pdp", "gdpr")):
        return "Relevan untuk kepatuhan pelindungan data, hak subjek data, dasar pemrosesan, dan tata kelola privasi."
    if any(x in t for x in ("artificial intelligence", "kecerdasan artifisial", "ai regulation")):
        return "Relevan untuk tata kelola AI, transparansi, akuntabilitas, dan pengawasan manusia."
    return "Relevan untuk perkembangan hukum, teknologi, dan media yang dapat memengaruhi kebijakan serta kepatuhan organisasi."


def choose_story(candidates: list[dict[str, Any]], history: list[dict[str, Any]]) -> dict[str, Any]:
    pool = [x for x in candidates if not duplicate(x["title"], history)]
    if not pool:
        raise RuntimeError("Tidak ada berita baru yang layak diposting.")
    pool.sort(key=score, reverse=True)
    selected = pool[0]
    selected["score"] = round(score(selected), 2)
    selected["impact"] = impact_line(selected["title"])
    return selected


def font(size: int, bold: bool = False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt, width: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = word if not line else f"{line} {word}"
        if draw.textbbox((0, 0), trial, font=fnt)[2] <= width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def render_card(story: dict[str, Any], output: Path) -> None:
    W, H = 1080, 1350
    img = Image.new("RGB", (W, H), (249, 248, 246))
    d = ImageDraw.Draw(img)
    navy, muted, maroon = (24, 34, 51), (94, 99, 109), (132, 46, 54)
    margin = 82

    d.text((margin, 70), "HUKUM • TEKNOLOGI • MEDIA", font=font(25), fill=maroon)
    d.line((margin, 118, 260, 118), fill=maroon, width=5)

    pub = datetime.fromisoformat(story["published_utc"]).astimezone(TZ)
    d.text((margin, 165), pub.strftime("%d %B %Y").upper(), font=font(25), fill=muted)

    title_f = font(63, True)
    max_w = W - 2 * margin
    title_lines = wrap(d, story["title"], title_f, max_w)
    while len(title_lines) > 7 and getattr(title_f, "size", 63) > 46:
        title_f = font(title_f.size - 4, True)
        title_lines = wrap(d, story["title"], title_f, max_w)

    y = 245
    for line in title_lines[:7]:
        d.text((margin, y), line, font=title_f, fill=navy)
        y += int(getattr(title_f, "size", 60) * 1.2)

    y += 30
    d.line((margin, y, W - margin, y), fill=(215, 216, 219), width=2)
    y += 40

    body_f = font(31)
    for line in wrap(d, story["impact"], body_f, max_w)[:5]:
        d.text((margin, y), line, font=body_f, fill=muted)
        y += 45

    footer_top = 1135
    d.line((margin, footer_top, W - margin, footer_top), fill=(215, 216, 219), width=2)
    d.text((margin, 1175), "Pusat Studi Hukum, Teknologi dan Media", font=font(29, True), fill=navy)
    d.text((margin, 1220), "IKA FH UNDIP", font=font(26), fill=maroon)
    d.text((margin, 1282), f"Sumber: {story['source']}"[:80], font=font(22), fill=muted)

    img.save(output, "JPEG", quality=94, optimize=True)


def caption(story: dict[str, Any]) -> str:
    pub = datetime.fromisoformat(story["published_utc"]).astimezone(TZ)
    return (
        f"{story['title']}\n\n{story['impact']}\n\n"
        f"Sumber: {story['source']}\nDipublikasikan: {pub.strftime('%d %B %Y, %H:%M WIB')}\n\n"
        "Pusat Studi Hukum, Teknologi dan Media | IKA FH UNDIP"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)
    history = load_history(Path(args.history))
    story = choose_story(fetch_candidates(), history)
    story["caption"] = caption(story)
    story["selected_at"] = datetime.now(TZ).isoformat()
    story["id"] = hashlib.sha256((story["title"] + story["link"]).encode()).hexdigest()[:16]
    render_card(story, outdir / "post.jpg")
    (outdir / "meta.json").write_text(json.dumps(story, ensure_ascii=False, indent=2), encoding="utf-8")

    cutoff = datetime.now(TZ) - timedelta(days=int(CONFIG.get("history_days", 14)))
    kept = []
    for item in history:
        try:
            dt = datetime.fromisoformat(item.get("selected_at", ""))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=TZ)
            if dt >= cutoff:
                kept.append(item)
        except Exception:
            pass
    kept.append({k: story[k] for k in ("id", "title", "source", "link", "selected_at")})
    (outdir / "history.next.json").write_text(json.dumps(kept, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
