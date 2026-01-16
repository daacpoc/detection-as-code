#!/usr/bin/env python3
"""Generate Sigma rules from a prompt file using the Poe API (OpenAI-compatible endpoint).

Poe provides an OpenAI-compatible chat completions API at:
  https://api.poe.com/v1/chat/completions citeturn2search5
Auth uses a Bearer token in the Authorization header. citeturn2search1

This script:
  - Reads a prompt markdown file (e.g. prompt.md)
  - Sends it to a model (default: Claude-Opus-4.5) via Poe
  - Expects the response to include one or more Sigma YAML rules
  - Writes each rule as a separate .yml file under rules/sigma/

Usage:
  python tools/poe_generate_sigma.py \
    --prompt prompt.md \
    --out-dir rules/sigma

Env vars:
  POE_API_KEY  (required unless --api-key passed)
  POE_MODEL    (default: Claude-Opus-4.5)
"""

from __future__ import annotations

import argparse
import os
import re
import time
from pathlib import Path
from typing import List

import requests

POE_BASE_URL = "https://api.poe.com/v1"
DEFAULT_MODEL = os.getenv("POE_MODEL", "Claude-Opus-4.5")


def _extract_yaml_blocks(text: str) -> List[str]:
    """Extract ```yaml ... ``` blocks if present; otherwise treat whole text as YAML."""
    blocks = re.findall(r"```(?:yaml|yml)\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    if blocks:
        return [b.strip() for b in blocks if b.strip()]
    # Fallback: heuristically split multiple docs
    parts = [p.strip() for p in text.split("\n---\n") if p.strip()]
    return parts if parts else [text.strip()]


def _safe_filename(yaml_text: str, fallback: str) -> str:
    # Try to find a Sigma id or title
    m = re.search(r"^id:\s*([a-f0-9\-]{8,})\s*$", yaml_text, flags=re.MULTILINE | re.IGNORECASE)
    if m:
        return m.group(1)
    m = re.search(r"^title:\s*(.+?)\s*$", yaml_text, flags=re.MULTILINE | re.IGNORECASE)
    if m:
        t = re.sub(r"[^a-zA-Z0-9_\-]+", "_", m.group(1).strip())
        return t[:80] if t else fallback
    return fallback


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True, help="Path to prompt file (markdown or text)")
    ap.add_argument("--out-dir", default="rules/sigma", help="Where to write generated Sigma YAML files")
    ap.add_argument("--api-key", default=os.getenv("POE_API_KEY", ""))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--max-tokens", type=int, default=4096)
    args = ap.parse_args()

    if not args.api_key:
        raise SystemExit("Missing POE_API_KEY (set env var or pass --api-key)")

    prompt_text = Path(args.prompt).read_text(encoding="utf-8")

    # Strong instruction to output Sigma YAML only.
    user_message = (
        "You are a senior detection engineer. "
        "Create one or more Sigma rules in valid Sigma YAML format. "
        "Return ONLY Sigma YAML. If multiple rules, separate them using '---'.\n\n"
        + prompt_text
    )

    payload = {
        "model": args.model,
        "messages": [{"role": "user", "content": user_message}],
        "max_tokens": args.max_tokens,
    }

    r = requests.post(
        f"{POE_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {args.api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=120,
    )
    r.raise_for_status()
    j = r.json()

    # OpenAI-compatible: choices[0].message.content
    content = (
        (j.get("choices") or [{}])[0]
        .get("message", {})
        .get("content")
    )
    if not content:
        raise RuntimeError(f"Unexpected Poe response: {j}")

    blocks = _extract_yaml_blocks(content)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    written = []
    ts = int(time.time())
    for idx, y in enumerate(blocks, start=1):
        name = _safe_filename(y, f"generated_{ts}_{idx}")
        out_path = out_dir / f"{name}.yml"
        out_path.write_text(y.strip() + "\n", encoding="utf-8")
        written.append(str(out_path))

    print("Wrote:")
    for p in written:
        print(f"  - {p}")


if __name__ == "__main__":
    main()
