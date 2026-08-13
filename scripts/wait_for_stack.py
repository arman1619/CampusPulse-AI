import argparse,time,urllib.request
parser=argparse.ArgumentParser();parser.add_argument("--url",default="http://localhost:8080");parser.add_argument("--timeout",type=int,default=180);args=parser.parse_args()
checks=["/gateway-health","/api/auth/health","/api/feedback/health","/api/ai/health","/api/notifications/health","/api/assistant/health","/api/assistant/ready"]
deadline=time.time()+args.timeout
while time.time()<deadline:
 ok=True
 for path in checks:
  try:
   with urllib.request.urlopen(args.url+path,timeout=3) as r: ok=ok and 200<=r.status<300
  except Exception:ok=False;break
 if ok:print("All gateway/service health checks passed.");raise SystemExit(0)
 time.sleep(3)
raise SystemExit("Timed out waiting for CampusPulse services")
