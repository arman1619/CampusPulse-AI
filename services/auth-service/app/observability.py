import json, logging, time, uuid
from datetime import datetime, timezone
from fastapi import Request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
HTTP_REQUESTS=Counter("campuspulse_http_requests_total","HTTP requests",["service","method","path","status"] )
HTTP_LATENCY=Histogram("campuspulse_http_request_duration_seconds","HTTP latency",["service","method","path"] )
def configure_logging(level="INFO"):
    logging.basicConfig(level=getattr(logging,level.upper(),logging.INFO),format="%(message)s")
class RequestContextMiddleware(BaseHTTPMiddleware):
    def __init__(self,app,service_name:str): super().__init__(app); self.service=service_name; self.log=logging.getLogger(service_name)
    async def dispatch(self,request:Request,call_next):
        rid=request.headers.get("X-Request-ID") or str(uuid.uuid4()); request.state.request_id=rid; start=time.perf_counter()
        try: response=await call_next(request)
        except Exception:
            self.log.exception(json.dumps({"timestamp":datetime.now(timezone.utc).isoformat(),"level":"ERROR","service":self.service,"request_id":rid,"method":request.method,"path":request.url.path,"event":"unhandled_exception"})); raise
        duration=time.perf_counter()-start; route=getattr(request.scope.get("route"),"path",request.url.path); HTTP_REQUESTS.labels(self.service,request.method,route,str(response.status_code)).inc(); HTTP_LATENCY.labels(self.service,request.method,route).observe(duration); response.headers["X-Request-ID"]=rid
        self.log.info(json.dumps({"timestamp":datetime.now(timezone.utc).isoformat(),"level":"INFO","service":self.service,"request_id":rid,"method":request.method,"path":request.url.path,"status_code":response.status_code,"duration_ms":round(duration*1000,2)})); return response
def metrics_response(): return Response(generate_latest(),media_type=CONTENT_TYPE_LATEST)
