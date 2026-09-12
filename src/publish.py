from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import requests


def req(method: str, url: str, **kwargs):
    r = requests.request(method, url, timeout=30, **kwargs)
    try:
        payload = r.json()
    except Exception:
        payload = {"raw": r.text[:1000]}
    if not r.ok:
        raise RuntimeError(f"Meta API {r.status_code}: {payload}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--meta", required=True)
    parser.add_argument("--image-url", required=True)
    args = parser.parse_args()

    ig_user_id = os.environ.get("IG_USER_ID", "").strip()
    token = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    version = os.environ.get("META_GRAPH_API_VERSION", "v26.0").strip()
    if not ig_user_id or not token:
        raise RuntimeError("IG_USER_ID atau IG_ACCESS_TOKEN belum tersedia.")

    meta = json.loads(Path(args.meta).read_text(encoding="utf-8"))
    base = f"https://graph.facebook.com/{version}"
    created = req("POST", f"{base}/{ig_user_id}/media", data={
        "image_url": args.image_url,
        "caption": meta["caption"],
        "access_token": token,
    })
    creation_id = created["id"]

    for _ in range(18):
        status = req("GET", f"{base}/{creation_id}", params={
            "fields": "status_code,status",
            "access_token": token,
        })
        if status.get("status_code") == "FINISHED":
            break
        if status.get("status_code") in {"ERROR", "EXPIRED"}:
            raise RuntimeError(f"Container gagal: {status}")
        time.sleep(5)
    else:
        raise RuntimeError("Container belum siap setelah 90 detik.")

    published = req("POST", f"{base}/{ig_user_id}/media_publish", data={
        "creation_id": creation_id,
        "access_token": token,
    })
    print(json.dumps({"published_media_id": published.get("id")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
