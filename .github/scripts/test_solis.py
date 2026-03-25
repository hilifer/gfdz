"""Test Solis Cloud API V2 connectivity — needs api_id and api_secret."""
import base64
import hashlib
import hmac
import json
from datetime import datetime, timezone
from email.utils import formatdate
from time import mktime

import httpx

# Solis credentials — currently empty, will fail gracefully
API_BASE = "https://www.soliscloud.com:13333"
API_ID = "1300386381677083058"
API_SECRET = "64ca50287e5e446988f6828ce4b16450"


def content_md5(body: bytes) -> str:
    return base64.b64encode(hashlib.md5(body).digest()).decode()


def sign(content_md5_val, content_type, date_str, path, api_secret):
    param = f"POST\n{content_md5_val}\n{content_type}\n{date_str}\n{path}"
    h = hmac.new(api_secret.encode(), param.encode(), hashlib.sha1)
    return base64.b64encode(h.digest()).decode()


def build_headers(body_bytes, path):
    ct = "application/json;charset=UTF-8"
    md5 = content_md5(body_bytes)
    now = datetime.now(tz=timezone.utc)
    date_str = formatdate(timeval=mktime(now.timetuple()), usegmt=True)
    sig = sign(md5, ct, date_str, path, API_SECRET)
    return {
        "Content-MD5": md5,
        "Content-Type": ct,
        "Date": date_str,
        "Authorization": f"API {API_ID}:{sig}",
    }


def main():
    if not API_ID or not API_SECRET:
        print("Solis API_ID and API_SECRET not configured — testing connectivity only")
        # Just test if the server is reachable
        try:
            client = httpx.Client(timeout=15, verify=False)
            resp = client.post(
                f"{API_BASE}/v1/api/userStationList",
                content=b'{"pageNo":1,"pageSize":1}',
                headers={"Content-Type": "application/json"},
            )
            print(f"Solis server reachable: status={resp.status_code}")
            print(f"Body: {resp.text[:500]}")
        except Exception as e:
            print(f"Solis server unreachable: {e}")
        return

    client = httpx.Client(timeout=30, verify=False)

    # 1. Station list
    print("=" * 60)
    print("TEST: Solis userStationList")
    print("=" * 60)
    path = "/v1/api/userStationList"
    body = json.dumps({"pageNo": 1, "pageSize": 10}).encode()
    headers = build_headers(body, path)
    resp = client.post(f"{API_BASE}{path}", content=body, headers=headers)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])

    # Extract stations
    stations = []
    if data.get("success"):
        page = data.get("data", {}).get("page", {})
        records = page.get("records", [])
        for s in records:
            stations.append(s)
            print(f"\nStation: {s.get('stationName')} id={s.get('id')}")

    if not stations:
        print("No stations found.")
        return

    # 2. Station detail
    sid = str(stations[0]["id"])
    print(f"\n{'=' * 60}")
    print(f"TEST: Solis stationDetail (id={sid})")
    print("=" * 60)
    path2 = "/v1/api/stationDetail"
    body2 = json.dumps({"id": sid}).encode()
    headers2 = build_headers(body2, path2)
    resp2 = client.post(f"{API_BASE}{path2}", content=body2, headers=headers2)
    print(f"Status: {resp2.status_code}")
    print(json.dumps(resp2.json(), indent=2, ensure_ascii=False)[:2000])

    # 3. Inverter list
    print(f"\n{'=' * 60}")
    print(f"TEST: Solis inverterList (stationId={sid})")
    print("=" * 60)
    path3 = "/v1/api/inverterList"
    body3 = json.dumps({"pageNo": 1, "pageSize": 10, "stationId": sid}).encode()
    headers3 = build_headers(body3, path3)
    resp3 = client.post(f"{API_BASE}{path3}", content=body3, headers=headers3)
    print(f"Status: {resp3.status_code}")
    print(json.dumps(resp3.json(), indent=2, ensure_ascii=False)[:2000])


if __name__ == "__main__":
    main()
