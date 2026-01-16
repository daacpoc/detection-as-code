#!/usr/bin/env python3
"""Convert Sigma YAML rules to Sumo Logic queries using a local sigconverter.io API.

This script is intentionally lightweight and CI-friendly.

Default converter endpoint is compatible with the public service URL pattern:
  https://sigconverter.io/api/v1/convert
In CI we typically run the converter locally and point SIGCONVERTER_URL to:
  http://localhost:8000/api/v1/convert

Because sigconverter.io's API surface can evolve, the endpoint and payload
are configurable.

Environment variables:
  SIGCONVERTER_URL   : conversion endpoint
  SIGCONVERTER_BACKEND: backend name (default: sumologic)

Usage:
  python tools/convert_sigma_to_sumo.py --sigma-dir rules/sigma --out-dir build/sumo_queries
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict

import requests

DEFAULT_URL = os.getenv("SIGCONVERTER_URL", "http://localhost:8000/api/v1/convert")
DEFAULT_BACKEND = os.getenv("SIGCONVERTER_BACKEND", "sumologic")


def _post_convert(url: str, sigma_text: str, backend: str) -> str:
    """Best-effort call.

    sigconverter.io doesn't publish a stable OpenAPI in the README, so we support
    two common payload styles:
      1) JSON payload: {"sigma": "<yaml>", "backend": "sumologic"}
      2) Form payload: sigma=<yaml>&backend=sumologic

    We'll try JSON first, then fall back to form.
    """

    headers = {"Accept": "application/json"}

    # Attempt JSON
    try:
        r = requests.post(
            url,
            headers={**headers, "Content-Type": "application/json"},
            data=json.dumps({"sigma": sigma_text, "backend": backend}),
            timeout=60,
        )
        if r.ok:
            # Expected shapes:
            #  - {"result": "..."}
            #  - {"data": "..."}
            #  - plain text
            try:
                j = r.json()
                return str(j.get("result") or j.get("data") or j.get("query") or r.text)
            except Exception:
                return r.text
    except Exception:
        pass

    # Fallback: form
    r = requests.post(url, data={"sigma": sigma_text, "backend": backend}, timeout=60)
    r.raise_for_status()
    try:
        j = r.json()
        return str(j.get("result") or j.get("data") or j.get("query") or r.text)
    except Exception:
        return r.text


def _safe_name(path: Path) -> str:
    return path.stem.replace(" ", "_")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sigma-dir", required=True, help="Directory containing Sigma YAML rules")
    ap.add_argument("--out-dir", required=True, help="Output directory for converted Sumo queries")
    ap.add_argument("--converter-url", default=DEFAULT_URL)
    ap.add_argument("--backend", default=DEFAULT_BACKEND)
    args = ap.parse_args()

    sigma_dir = Path(args.sigma_dir)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not sigma_dir.exists():
        print(f"Sigma dir not found: {sigma_dir} (nothing to convert)")
        return

    sigma_files = sorted(list(sigma_dir.glob("**/*.yml")) + list(sigma_dir.glob("**/*.yaml")))
    if not sigma_files:
        print(f"No Sigma files found under {sigma_dir} (nothing to convert)")
        return

    results: Dict[str, Dict[str, Any]] = {}
    for f in sigma_files:
        sigma_text = f.read_text(encoding="utf-8")
        try:
            query = _post_convert(args.converter_url, sigma_text, args.backend)
            out_path = out_dir / f"{_safe_name(f)}.sumo.query"
            out_path.write_text(query.strip() + "\n", encoding="utf-8")
            results[str(f)] = {"ok": True, "out": str(out_path)}
            print(f"[OK] {f} -> {out_path}")
        except Exception as e:
            results[str(f)] = {"ok": False, "error": str(e)}
            print(f"[FAIL] {f}: {e}")

    # Write a small manifest for CI visibility
    (out_dir / "manifest.json").write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
