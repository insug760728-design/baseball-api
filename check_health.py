import urllib.request
import json
import sys
import time

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def check_health(host="http://127.0.0.1:8000"):
    print(f"[CHECK] Checking health status on {host} ...")
    start = time.time()
    try:
        req = urllib.request.Request(f"{host}/healthz", headers={"User-Agent": "HealthCheckClient/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            elapsed = round((time.time() - start) * 1000, 1)
            if resp.status == 200:
                data = json.loads(resp.read().decode())
                print(f"[SUCCESS] Status: {resp.status} OK | Latency: {elapsed}ms | Service: {data.get('service')}")
                return True
            else:
                print(f"[WARNING] Unexpected status code: {resp.status}")
                return False
    except Exception as e:
        print(f"[FAIL] Health check failed: {e}")
        return False

if __name__ == '__main__':
    ok = check_health()
    sys.exit(0 if ok else 1)
