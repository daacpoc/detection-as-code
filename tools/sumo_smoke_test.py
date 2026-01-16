#!/usr/bin/env python3
"""Sumo Logic smoke tests for detections.

What this does:
  1) Ingest local test log files into a Sumo HTTP Source (Hosted Collector HTTP Logs & Metrics source).
  2) Run one or more searches via the Sumo Search Job API.
  3) Assert basic expectations (e.g., at least N matches).

Why it's useful:
  - Validates that queries parse and return expected results on known data.
  - Provides quick confidence before Terraform apply.

Docs:
  - Search Job API: POST /v1/search/jobs citeturn3search0
  - Upload logs to HTTP source: Sumo HTTP Source receives logs at its unique URL citeturn3search7turn3search14

Auth:
  - Sumo APIs support access id/key authentication citeturn3search2

Config file format (YAML):

  source_category: "ci/detections"   # used as X-Sumo-Category header for ingestion
  default_time_window_minutes: 15
  tests:
    - name: "Windows user account event"
      log_file: "tests/winevent-4720-log-snip.log"
      query: "_sourceCategory=ci/detections \"EventCode=4738\""
      min_results: 1

Notes:
  - If your log file is multi-line, we send it as-is. Sumo HTTP source will ingest it as lines.
  - Keep queries tight (use sourceCategory and a short time window) to avoid scanning your whole account.
"""

from __future__ import annotations

import argparse
import base64
import json
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import yaml


@dataclass
class SmokeTest:
    name: str
    log_file: str
    query: str
    min_results: int = 1


def _basic_auth_header(access_id: str, access_key: str) -> str:
    token = base64.b64encode(f"{access_id}:{access_key}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def _ingest_log(http_source_url: str, log_text: str, source_category: str) -> None:
    # Sumo HTTP Sources accept logs at a unique URL citeturn3search7turn3search14
    headers = {
        "Content-Type": "text/plain",
        "X-Sumo-Category": source_category,
    }
    r = requests.post(http_source_url, data=log_text.encode("utf-8"), headers=headers, timeout=60)
    r.raise_for_status()


def _create_search_job(api_base_url: str, auth_header: str, query: str, from_ms: int, to_ms: int) -> str:
    # Create a search job: POST /v1/search/jobs citeturn3search0
    url = api_base_url.rstrip("/") + "/v1/search/jobs"
    payload = {
        "query": query,
        "from": str(from_ms),
        "to": str(to_ms),
        "timeZone": "UTC",
    }
    r = requests.post(
        url,
        headers={"Authorization": auth_header, "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=60,
    )
    r.raise_for_status()
    j = r.json()
    # Typical response includes an id
    job_id = j.get("id") or j.get("data", {}).get("id")
    if not job_id:
        raise RuntimeError(f"Unexpected create-job response: {j}")
    return str(job_id)


def _wait_job_done(api_base_url: str, auth_header: str, job_id: str, timeout_s: int = 120) -> Dict[str, Any]:
    url = api_base_url.rstrip("/") + f"/v1/search/jobs/{job_id}"
    start = time.time()
    last = None
    while time.time() - start < timeout_s:
        r = requests.get(url, headers={"Authorization": auth_header}, timeout=30)
        r.raise_for_status()
        j = r.json()
        last = j
        state = (j.get("state") or j.get("data", {}).get("state") or "").lower()
        if state in {"done", "canceled", "failed"}:
            return j
        time.sleep(2)
    raise TimeoutError(f"Search job {job_id} did not complete in {timeout_s}s. Last: {last}")


def _get_record_count(api_base_url: str, auth_header: str, job_id: str) -> int:
    # Many Sumo responses include messageCount/recordCount. If not, fall back to a messages endpoint.
    job = _wait_job_done(api_base_url, auth_header, job_id)
    for key in ("messageCount", "recordCount"):
        if key in job:
            return int(job[key])
        if "data" in job and key in job["data"]:
            return int(job["data"][key])

    # Fallback: fetch one page of messages and count them.
    # (Endpoint shape varies; this is best-effort.)
    url = api_base_url.rstrip("/") + f"/v1/search/jobs/{job_id}/messages?limit=1"
    r = requests.get(url, headers={"Authorization": auth_header}, timeout=30)
    r.raise_for_status()
    j = r.json()
    if "messageCount" in j:
        return int(j["messageCount"])
    if "data" in j and "messageCount" in j["data"]:
        return int(j["data"]["messageCount"])
    # If we truly can't determine, treat as 0
    return 0


def _load_config(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sumo-api-base-url", required=True, help="Example: https://api.us1.sumologic.com/api")
    ap.add_argument("--sumo-access-id", required=True)
    ap.add_argument("--sumo-access-key", required=True)
    ap.add_argument("--http-source-url", required=True, help="Hosted Collector HTTP Source URL")
    ap.add_argument("--smoke-config", required=True, help="YAML config file, e.g. tests/smoke-tests.yml")
    ap.add_argument("--out", required=True, help="Write results JSON here")
    args = ap.parse_args()

    cfg = _load_config(Path(args.smoke_config))
    source_category = cfg.get("source_category", "ci/detections")
    window_min = int(cfg.get("default_time_window_minutes", 15))

    tests: List[SmokeTest] = []
    for t in cfg.get("tests", []):
        tests.append(
            SmokeTest(
                name=t["name"],
                log_file=t["log_file"],
                query=t["query"],
                min_results=int(t.get("min_results", 1)),
            )
        )

    auth = _basic_auth_header(args.sumo_access_id, args.sumo_access_key)

    results: Dict[str, Any] = {
        "source_category": source_category,
        "window_minutes": window_min,
        "tests": [],
    }

    # Ingest all logs first (so a single time window works)
    for t in tests:
        log_path = Path(t.log_file)
        if not log_path.exists():
            results["tests"].append({"name": t.name, "ok": False, "error": f"Missing log file: {t.log_file}"})
            continue
        _ingest_log(args.http_source_url, log_path.read_text(encoding="utf-8", errors="replace"), source_category)

    # Give Sumo a brief moment to index
    time.sleep(int(cfg.get("post_ingest_sleep_seconds", 15)))

    now = datetime.now(timezone.utc)
    from_ts = int((now - timedelta(minutes=window_min)).timestamp() * 1000)
    to_ts = int(now.timestamp() * 1000)

    for t in tests:
        entry: Dict[str, Any] = {"name": t.name, "query": t.query, "min_results": t.min_results}
        try:
            job_id = _create_search_job(args.sumo_api_base_url, auth, t.query, from_ts, to_ts)
            count = _get_record_count(args.sumo_api_base_url, auth, job_id)
            entry.update({"job_id": job_id, "count": count, "ok": count >= t.min_results})
            if count < t.min_results:
                entry["error"] = f"Expected >= {t.min_results} results, got {count}"
        except Exception as e:
            entry.update({"ok": False, "error": str(e)})
        results["tests"].append(entry)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(results, indent=2), encoding="utf-8")

    # Fail CI if any test fails
    failed = [t for t in results["tests"] if not t.get("ok")]
    if failed:
        names = ", ".join(f["name"] for f in failed)
        raise SystemExit(f"Smoke tests failed: {names}")


if __name__ == "__main__":
    main()
