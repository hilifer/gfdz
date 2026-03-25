"""Test AiSWEI API connectivity and data retrieval."""
import base64
import hashlib
import hmac
import json
import time
import uuid
from urllib.parse import urlencode

import httpx

API_BASE = "http://api.general.aisweicloud.com"
TOKEN = "R3dBOTVXeUdGRDBTTmJvMjZyNDF0QT09"
APP_KEY = "204929444"
APP_SECRET = "S9eyOBeTqUn56eAn5XovdjbDVMef6lRE"


def sign_request(method, path_with_query, app_key, app_secret, accept="application/json"):
    timestamp = str(int(time.time() * 1000))
    nonce = uuid.uuid4().hex

    sign_headers = {
        "X-Ca-Key": app_key,
        "X-Ca-Stage": "RELEASE",
        "X-Ca-Timestamp": timestamp,
        "X-Ca-Version": "1",
    }
    sorted_keys = sorted(sign_headers.keys())
    headers_str = "\n".join(f"{k}:{sign_headers[k]}" for k in sorted_keys)

    string_to_sign = "\n".join([
        method.upper(),
        accept,
        "",  # content_md5
        "",  # content_type
        "",  # date
        headers_str + "\n" + path_with_query,
    ])

    signature = base64.b64encode(
        hmac.new(app_secret.encode(), string_to_sign.encode(), hashlib.sha256).digest()
    ).decode()

    return {
        "Accept": accept,
        "X-Ca-Key": app_key,
        "X-Ca-Timestamp": timestamp,
        "X-Ca-Nonce": nonce,
        "X-Ca-Stage": "RELEASE",
        "X-Ca-Version": "1",
        "X-Ca-Signature-Headers": ",".join(sorted_keys),
        "X-Ca-Signature": signature,
    }


def build_url(path, params):
    sorted_params = sorted(params.items())
    qs = urlencode(sorted_params, doseq=True)
    return f"{path}?{qs}" if qs else path


def main():
    client = httpx.Client(timeout=30)

    # 1. Get station list
    print("=" * 60)
    print("TEST: AiSWEI getPlanListPro")
    print("=" * 60)
    params = {"order": "0", "pageNum": "1", "pageSize": "10", "token": TOKEN}
    full_path = build_url("/pro/getPlanListPro", params)
    headers = sign_request("GET", full_path, APP_KEY, APP_SECRET)
    resp = client.get(f"{API_BASE}{full_path}", headers=headers)
    print(f"Status: {resp.status_code}")
    body = resp.json()
    print(json.dumps(body, indent=2, ensure_ascii=False)[:2000])

    # Extract station apikeys for further testing
    stations = []
    if body.get("status") == 200 or body.get("code") == 0:
        data = body.get("data") or {}
        result = data.get("result") or []
        for s in result:
            stations.append(s)
            print(f"\nStation: {s.get('name')} apikey={s.get('apikey')} power={s.get('totalpower')}")

    if not stations:
        print("No stations found, stopping.")
        return

    # 2. Get device list for first station
    apikey = stations[0].get("apikey", "")
    print(f"\n{'=' * 60}")
    print(f"TEST: AiSWEI getDeviceListPro (apikey={apikey})")
    print("=" * 60)
    params2 = {"apikey": apikey, "token": TOKEN}
    full_path2 = build_url("/pro/getDeviceListPro", params2)
    headers2 = sign_request("GET", full_path2, APP_KEY, APP_SECRET)
    resp2 = client.get(f"{API_BASE}{full_path2}", headers=headers2)
    print(f"Status: {resp2.status_code}")
    print(json.dumps(resp2.json(), indent=2, ensure_ascii=False)[:2000])

    # 3. Get plant overview
    print(f"\n{'=' * 60}")
    print(f"TEST: AiSWEI getPlantOverviewPro (apikey={apikey})")
    print("=" * 60)
    params3 = {"apikey": apikey, "token": TOKEN}
    full_path3 = build_url("/pro/getPlantOverviewPro", params3)
    headers3 = sign_request("GET", full_path3, APP_KEY, APP_SECRET)
    resp3 = client.get(f"{API_BASE}{full_path3}", headers=headers3)
    print(f"Status: {resp3.status_code}")
    print(json.dumps(resp3.json(), indent=2, ensure_ascii=False)[:2000])

    # 4. Get last ts data for first inverter
    devices_body = resp2.json()
    device_data = devices_body.get("data") or []
    isn = None
    for group in device_data:
        for inv in group.get("inverters") or []:
            isn = inv.get("isn")
            break
        if isn:
            break

    if isn:
        print(f"\n{'=' * 60}")
        print(f"TEST: AiSWEI getLastTsDataPro (isn={isn})")
        print("=" * 60)
        params4 = {"isnos": isn, "token": TOKEN}
        full_path4 = build_url("/pro/getLastTsDataPro", params4)
        headers4 = sign_request("GET", full_path4, APP_KEY, APP_SECRET)
        resp4 = client.get(f"{API_BASE}{full_path4}", headers=headers4)
        print(f"Status: {resp4.status_code}")
        print(json.dumps(resp4.json(), indent=2, ensure_ascii=False)[:3000])


if __name__ == "__main__":
    main()
