#!/usr/bin/env python3
"""
Wayback Machine (Internet Archive) Save Page Now 2 Backup Script
Conservative rate-limited version (6s delay, robust retry)
"""

import os
import sys
import time
import json
import logging
from pathlib import Path
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

BASE_DIR = Path(__file__).resolve().parent.parent
URLS_FILE = BASE_DIR / "urls.txt"
DATA_DIR = BASE_DIR / "data"
STATUS_FILE = DATA_DIR / "wayback-status.json"
ENV_FILE = BASE_DIR / ".env"

SPN_SAVE_URL = "https://web.archive.org/save/"
SPN_STATUS_URL = "https://web.archive.org/save/status/"

def load_env():
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    if key not in os.environ:
                        os.environ[key] = val

def get_credentials():
    load_env()
    access_key = os.environ.get("IA_ACCESS_KEY", "").strip()
    secret_key = os.environ.get("IA_SECRET_KEY", "").strip()
    return access_key, secret_key

def load_urls():
    if not URLS_FILE.exists():
        manifest_file = BASE_DIR / "manifest.json"
        if manifest_file.exists():
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            return [item["source_url"] for item in manifest.get("items", [])]
        else:
            raise FileNotFoundError(f"Neither {URLS_FILE} nor {manifest_file} found.")
    
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return urls

def load_status():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if STATUS_FILE.exists():
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.warning(f"Failed to read existing status file: {e}. Starting fresh.")
    return {
        "updated_at": "",
        "total_targets": 0,
        "success_count": 0,
        "failed_count": 0,
        "records": {}
    }

def save_status(status_data):
    status_data["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    status_data["success_count"] = sum(1 for r in status_data["records"].values() if r.get("status") == "success")
    status_data["failed_count"] = sum(1 for r in status_data["records"].values() if r.get("status") in ("error", "failed", "timeout"))
    status_data["total_records"] = len(status_data["records"])
    
    tmp_file = STATUS_FILE.with_suffix(".tmp")
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(status_data, f, ensure_ascii=False, indent=2)
    tmp_file.replace(STATUS_FILE)

def check_job_status(job_id, headers, timeout=90, poll_interval=5):
    start_time = time.time()
    url = f"{SPN_STATUS_URL}{job_id}"
    while time.time() - start_time < timeout:
        try:
            resp = requests.get(url, headers=headers, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                status = data.get("status")
                if status == "success":
                    return "success", data
                elif status == "error":
                    return "error", data
                elif status == "pending":
                    time.sleep(poll_interval)
                    continue
                else:
                    return status, data
            elif resp.status_code == 429:
                logging.warning("Rate limit on status poll. Waiting 20s...")
                time.sleep(20)
            else:
                time.sleep(poll_interval)
        except Exception as e:
            logging.warning(f"Connection glitch polling {job_id}: {e}. Waiting 10s...")
            time.sleep(10)
            
    return "timeout", {"message": f"Polling timed out after {timeout} seconds"}

def archive_url(target_url, access_key, secret_key, max_retries=3):
    headers = {
        "Accept": "application/json",
        "Authorization": f"LOW {access_key}:{secret_key}",
    }
    payload = {
        "url": target_url,
        "capture_outlinks": 0,
        "if_not_archived_within": "7d",
        "skip_first_archive": 1
    }

    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(SPN_SAVE_URL, headers=headers, data=payload, timeout=25)
            if resp.status_code == 200:
                res_data = resp.json()
                job_id = res_data.get("job_id")
                if job_id:
                    status, details = check_job_status(job_id, headers)
                    return {
                        "status": status,
                        "job_id": job_id,
                        "details": details,
                        "snapshot_url": f"https://web.archive.org/web/{details.get('timestamp')}/{target_url}" if details.get("timestamp") else None
                    }
                else:
                    return {"status": "success", "details": res_data}
            elif resp.status_code == 429:
                wait_sec = 40 * (attempt + 1)
                logging.warning(f"Rate limited (429) on save. Waiting {wait_sec}s...")
                time.sleep(wait_sec)
                continue
            else:
                return {
                    "status": "error",
                    "http_status": resp.status_code,
                    "error_message": resp.text[:200]
                }
        except Exception as e:
            if attempt < max_retries:
                logging.warning(f"Glitch saving {target_url}: {e}. Retrying in 15s...")
                time.sleep(15)
                continue
            return {"status": "error", "error_message": str(e)}

    return {"status": "error", "error_message": "Exceeded maximum retries"}

def main():
    access_key, secret_key = get_credentials()
    if not access_key or not secret_key:
        logging.error("Missing IA keys.")
        sys.exit(1)

    urls = load_urls()
    status_data = load_status()
    status_data["total_targets"] = len(urls)

    logging.info(f"Wayback archive process starting for {len(urls)} URLs (Conservative 6s spacing)...")
    
    # Clean up any transient error from previous connection reset
    for u, rec in list(status_data["records"].items()):
        if rec.get("status") in ("error", "failed", "timeout"):
            del status_data["records"][u]
    save_status(status_data)

    success_count = sum(1 for r in status_data["records"].values() if r.get("status") == "success")
    logging.info(f"Already successful: {success_count}/{len(urls)}")

    for idx, url in enumerate(urls, 1):
        existing = status_data["records"].get(url)
        if existing and existing.get("status") == "success":
            logging.info(f"[{idx}/{len(urls)}] Skipping (already archived): {url}")
            continue

        logging.info(f"[{idx}/{len(urls)}] Archiving: {url}")
        result = archive_url(url, access_key, secret_key)
        
        status_data["records"][url] = {
            "url": url,
            "checked_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            **result
        }
        save_status(status_data)

        if result.get("status") == "success":
            logging.info(f" -> SUCCESS: {url}")
        else:
            logging.warning(f" -> FAILED ({result.get('status')}): {result.get('error_message') or result.get('details')}")

        # Conservative delay between requests to stay well below 15 req/min
        time.sleep(6)

    save_status(status_data)
    logging.info("=" * 60)
    logging.info(f"Batch completed! Success: {status_data['success_count']}/{len(urls)}")
    logging.info("=" * 60)

if __name__ == "__main__":
    main()
