#!/usr/bin/env python3
"""Generate ecommerce image sets through the OKM image API."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


DEFAULT_ENDPOINT = "https://okmcode.com/v1/images/generations"
DEFAULT_MODEL = "gpt-image-2"
ALLOWED_ENDPOINT_HOSTS = {"okmcode.com"}


def fail(message: str) -> None:
    raise SystemExit(f"generate_okm_images failed: {message}")


def detect_extension(data: bytes) -> str:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "webp"
    return "bin"


def safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._-")
    return cleaned or "image"


def validate_endpoint(endpoint: str, allow_custom_endpoint: bool) -> str:
    parsed = urllib.parse.urlparse(endpoint)
    if parsed.scheme != "https":
        fail("endpoint must use https")
    if not parsed.netloc:
        fail("endpoint is missing a host")
    if not allow_custom_endpoint and parsed.hostname not in ALLOWED_ENDPOINT_HOSTS:
        fail("custom endpoint blocked; pass --allow-custom-endpoint only if you trust the endpoint")
    return endpoint


def load_auth_key(env_name: str) -> str:
    for name in (env_name, "OKM_API_KEY", "OPENAI_API_KEY"):
        value = os.environ.get(name)
        if value:
            return value

    auth_path = Path.home() / ".codex" / "auth.json"
    if auth_path.exists():
        try:
            data = json.loads(auth_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(f"invalid auth file {auth_path}: {exc}")
        for name in (env_name, "OKM_API_KEY", "OPENAI_API_KEY"):
            value = data.get(name)
            if value:
                return str(value)

    fail(f"missing API key: set {env_name}, OKM_API_KEY, or OPENAI_API_KEY")


def load_jobs(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"jobs file not found: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid jobs JSON: {exc}")

    jobs = data.get("jobs", data) if isinstance(data, dict) else data
    if not isinstance(jobs, list) or not jobs:
        fail("jobs file must contain a non-empty list or {'jobs': [...]}")

    normalized = []
    for index, job in enumerate(jobs, 1):
        if not isinstance(job, dict):
            fail(f"job {index} must be an object")
        name = safe_filename(str(job.get("name") or f"{index:02d}_image"))
        prompt = str(job.get("prompt") or "").strip()
        if not prompt:
            fail(f"job {index} has no prompt")
        normalized.append({"name": name, "prompt": prompt})
    return normalized


def request_image(api_key: str, prompt: str, size: str, quality: str, model: str, endpoint: str) -> bytes:
    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "quality": quality,
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "codex-cli",
        },
        method="POST",
    )

    context = ssl.create_default_context()
    try:
        with urllib.request.urlopen(request, timeout=300, context=context) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            details = exc.read().decode("utf-8", errors="replace")
        except Exception:
            details = ""
        fail(f"HTTP {exc.code}: {details}")

    item = (body.get("data") or [{}])[0]
    if item.get("b64_json"):
        return base64.b64decode(item["b64_json"])
    if item.get("url"):
        with urllib.request.urlopen(item["url"], timeout=300, context=context) as image_response:
            return image_response.read()
    fail(f"unexpected response: {json.dumps(body, ensure_ascii=False)[:600]}")


def build_contact_sheet(paths: list[Path], out: Path) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageOps
    except Exception:
        return

    if not paths:
        return
    thumb_w, thumb_h, label_h = 320, 320, 36
    cols = 3
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGB", (thumb_w * cols, (thumb_h + label_h) * rows), (244, 248, 247))
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Avenir Next.ttc", 18)
    except Exception:
        font = ImageFont.load_default()

    for index, path in enumerate(paths):
        img = Image.open(path).convert("RGB")
        img = ImageOps.fit(img, (thumb_w, thumb_h), method=Image.Resampling.LANCZOS)
        tile = Image.new("RGB", (thumb_w, thumb_h + label_h), "white")
        tile.paste(img, (0, 0))
        draw = ImageDraw.Draw(tile)
        draw.text((10, thumb_h + 8), path.stem, font=font, fill=(55, 70, 72))
        sheet.paste(tile, ((index % cols) * thumb_w, (index // cols) * (thumb_h + label_h)))
    sheet.save(out, quality=94)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate image jobs through OKM.")
    parser.add_argument("--jobs", required=True, type=Path, help="JSON list of {'name','prompt'} jobs")
    parser.add_argument("--out", required=True, type=Path, help="Output directory")
    parser.add_argument("--size", default="1024x1024")
    parser.add_argument("--quality", default="high")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--allow-custom-endpoint", action="store_true")
    parser.add_argument("--api-key-env", default="OKM_API_KEY")
    parser.add_argument("--delay", type=float, default=1.0)
    args = parser.parse_args()

    api_key = load_auth_key(args.api_key_env)
    jobs = load_jobs(args.jobs)
    endpoint = validate_endpoint(args.endpoint, args.allow_custom_endpoint)
    args.out.mkdir(parents=True, exist_ok=True)

    outputs = []
    for job in jobs:
        image_bytes = request_image(api_key, job["prompt"], args.size, args.quality, args.model, endpoint)
        ext = detect_extension(image_bytes)
        path = args.out / f"{job['name']}.{ext}"
        path.write_bytes(image_bytes)
        record = {"name": job["name"], "path": str(path), "bytes": len(image_bytes)}
        outputs.append(record)
        print(json.dumps(record, ensure_ascii=False), flush=True)
        time.sleep(args.delay)

    (args.out / "okm_generation_results.json").write_text(
        json.dumps(outputs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    build_contact_sheet([Path(item["path"]) for item in outputs], args.out / "contact_sheet.jpg")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
