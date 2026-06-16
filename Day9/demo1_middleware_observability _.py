
# -*- coding: utf-8 -*-
"""
demo1_extensions.py
EY Backend Engineering Bootcamp — Day 9
All 4 Extension Tasks in one file.

Extension A — Sliding-window rate limiter middleware     (lines ~40)
Extension B — Correlation ID propagation via ContextVar (lines ~90)
Extension C — Prometheus metrics + Grafana config       (lines ~150)
Extension D — Structured NDJSON log aggregation         (lines ~210)
"""

# ── Shared imports ────────────────────────────────────────────────────────────
import uuid, time, json, random, asyncio, collections, logging
import contextvars
from pathlib import Path
from datetime import datetime, timezone

import structlog, httpx, pybreaker
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from prometheus_client import (
    Counter, Histogram, Gauge,
    generate_latest, CONTENT_TYPE_LATEST,
)

# =============================================================================
# EXTENSION A — Sliding-window Rate Limiter

RATE_LIMIT_HITS = Counter(
    "rate_limit_hits_total",
    "Requests rejected by rate limiter",
    ["client_ip"],
)
_windows: dict[str, collections.deque] = {}
LIMIT, WINDOW_S = 100, 60          # 100 req / 60 s per IP

def is_rate_limited(ip: str) -> tuple[bool, int]:
    now = time.monotonic()
    dq  = _windows.setdefault(ip, collections.deque())
    while dq and now - dq[0] > WINDOW_S:
        dq.popleft()
    if len(dq) >= LIMIT:
        return True, int(WINDOW_S - (now - dq[0])) + 1
    dq.append(now)
    return False, 0


# EXTENSION B — Correlation ID ContextVar + httpx propagation

correlation_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id", default=""
)

def inject_correlation_id(req: httpx.Request) -> None:
    corr = correlation_id_var.get("")
    if corr:
        req.headers["X-Correlation-Id"] = corr

def make_http_client() -> httpx.AsyncClient:
    """Every client created here auto-injects the correlation ID."""
    return httpx.AsyncClient(event_hooks={"request": [inject_correlation_id]})


# EXTENSION C — Prometheus 4 Golden Signals

REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "Request latency",
    ["method", "path"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
)
ACTIVE_REQUESTS = Gauge("http_active_requests", "In-flight requests")
CB_STATE        = Gauge(
    "circuit_breaker_state",
    "CB state (0=closed 1=open 2=half-open)",
    ["name"],
)
PAYMENT_AMOUNT  = Histogram(
    "payment_amount_gbp", "Payment amount GBP",
    buckets=[10, 50, 100, 500, 1000, 5000, 10000],
)

CB_STATE_MAP = {"closed": 0, "open": 1, "half-open": 2}

class CBMetricListener(pybreaker.CircuitBreakerListener):
    def state_change(self, cb, old, new):
        CB_STATE.labels(name=cb.name).set(CB_STATE_MAP.get(str(new), 0))

fraud_cb = pybreaker.CircuitBreaker(
    fail_max=3, reset_timeout=30,
    listeners=[CBMetricListener()], name="fraud-api",
)

GRAFANA_DASHBOARD = {
    "title": "EY Payment API — 4 Golden Signals",
    "panels": [
        {"title": "Request Rate (req/s)",   "targets": [{"expr": "rate(http_requests_total[1m])"}]},
        {"title": "p99 Latency (ms)",        "targets": [{"expr": "histogram_quantile(0.99,rate(http_request_duration_seconds_bucket[5m]))*1000"}]},
        {"title": "Error Rate (%)",          "targets": [{"expr": "sum(rate(http_requests_total{status=~'5..'}[5m]))/sum(rate(http_requests_total[5m]))*100"}]},
        {"title": "Circuit Breaker State",   "targets": [{"expr": "circuit_breaker_state"}]},
    ],
}

PROMETHEUS_YML = """
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'payment-api'
    static_configs:
      - targets: ['host.docker.internal:8000']
    metrics_path: /metrics
"""

# EXTENSION D — NDJSON Structured Log Aggregation
LOG_DIR  = Path("logs")
LOG_FILE = LOG_DIR / "app.log"
LOG_DIR.mkdir(exist_ok=True)

_file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
_file_handler.setFormatter(logging.Formatter("%(message)s"))
logging.getLogger().addHandler(_file_handler)
logging.getLogger().setLevel(logging.DEBUG)

# TO THIS:
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.BoundLogger,
    logger_factory=structlog.PrintLoggerFactory(),
)
log = structlog.get_logger()

class LogQuery:
    def __init__(self, path: Path = LOG_FILE):
        self.lines = self._load(path)

    def _load(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        records = []
        for raw in path.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            try:
                idx = raw.index("{")
                records.append(json.loads(raw[idx:]))
            except (ValueError, json.JSONDecodeError):
                pass
        return records

    def where(self, **kw) -> "LogQuery":
        return self._clone([r for r in self.lines if all(r.get(k)==v for k,v in kw.items())])

    def where_gt(self, field: str, value: float) -> "LogQuery":
        return self._clone([r for r in self.lines if r.get(field, 0) > value])

    def select(self, *fields) -> list[dict]:
        return [{f: r.get(f) for f in fields} for r in self.lines]

    def count(self) -> int:
        return len(self.lines)

    def _clone(self, lines) -> "LogQuery":
        q = LogQuery.__new__(LogQuery)
        q.lines = lines
        return q

# =============================================================================
# FASTAPI APP — all middleware + routes wired together
# =============================================================================
app = FastAPI(title="EY Payment API — Extensions A–D", version="2.0.0")

# ── Middleware A: Rate limiter ─────────────────────────────────────────────
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    ip = request.client.host or "unknown"
    limited, retry_after = is_rate_limited(ip)
    if limited:
        RATE_LIMIT_HITS.labels(client_ip=ip).inc()
        return JSONResponse(
            status_code=429,
            content={"error": "Too Many Requests",
                     "retry_after_seconds": retry_after},
            headers={"Retry-After": str(retry_after)},
        )
    return await call_next(request)

# ── Middleware B: Correlation ID ContextVar ────────────────────────────────
@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    corr_id = request.headers.get("X-Correlation-Id", str(uuid.uuid4()))
    token   = correlation_id_var.set(corr_id)
    try:
        response = await call_next(request)
        response.headers["X-Correlation-Id"] = corr_id
        return response
    finally:
        correlation_id_var.reset(token)

# ── Middleware C: Prometheus metrics ───────────────────────────────────────
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    ACTIVE_REQUESTS.inc()
    start    = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    REQUEST_COUNT.labels(method=request.method,
                         path=request.url.path,
                         status=response.status_code).inc()
    REQUEST_LATENCY.labels(method=request.method,
                           path=request.url.path).observe(duration)
    ACTIVE_REQUESTS.dec()
    return response

# ── Middleware D: Structured logging ──────────────────────────────────────
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start   = time.perf_counter()
    corr_id = correlation_id_var.get(str(uuid.uuid4()))
    log.info("request.started", path=request.url.path,
             method=request.method, correlation_id=corr_id)
    response    = await call_next(request)
    latency_ms  = round((time.perf_counter() - start) * 1000, 2)
    log.info("request.completed", path=request.url.path,
             status=response.status_code, latency_ms=latency_ms,
             correlation_id=corr_id)
    return response

# ── Routes ────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "extensions": ["A-rate-limit","B-corr-id","C-prometheus","D-logging"]}

@app.post("/payments")
async def create_payment(request: Request):
    body   = await request.json()
    amount = float(body.get("amount", 0))
    PAYMENT_AMOUNT.observe(amount)
    async with make_http_client() as client:
        fraud = await client.get("http://localhost:8000/downstream/fraud-check")
    return {"payment_id": str(uuid.uuid4()), "status": "accepted",
            "fraud": fraud.json(), **body}

@app.get("/downstream/fraud-check")
async def mock_fraud_check(request: Request):
    received_corr = request.headers.get("X-Correlation-Id", "MISSING")
    return {"fraud_score": 0.02, "decision": "approved",
            "received_correlation_id": received_corr}

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/logs/query")
async def query_logs(latency_gt: float = 0.0, status: int = None):
    q = LogQuery()
    if latency_gt:
        q = q.where_gt("latency_ms", latency_gt)
    if status:
        q = q.where(status=status)
    return {"count": q.count(), "results": q.select("path","latency_ms","status","correlation_id")}


# STANDALONE DEMOS (python demo1_extensions.py)

if __name__ == "__main__":
    print("=" * 60)
    print("EXTENSION A — Rate Limiter (limit=10 for demo)")
    print("=" * 60)
    LIMIT = 10
    for i in range(13):
        limited, retry = is_rate_limited("10.0.0.1")
        status = f"🔴 429  Retry-After:{retry}s" if limited else "✅ 200  OK"
        print(f"  Request {i+1:>2}: {status}")

    print("\n" + "=" * 60)
    print("EXTENSION B — ContextVar isolation (5 concurrent requests)")
    print("=" * 60)
    async def sim_request(n):
        corr  = f"corr-{n}-{uuid.uuid4().hex[:6]}"
        token = correlation_id_var.set(corr)
        try:
            await asyncio.sleep(0.01)
            got   = correlation_id_var.get()
            match = "✅" if got == corr else "❌"
            print(f"  Request {n}: set={corr} got={got} {match}")
        finally:
            correlation_id_var.reset(token)

    async def run_all(): await asyncio.gather(*[sim_request(i) for i in range(1, 6)])
    asyncio.run(run_all())

    print("\n" + "=" * 60)
    print("EXTENSION C — Prometheus metrics simulation")
    print("=" * 60)
    for i in range(5):
        REQUEST_COUNT.labels(method="POST", path="/payments", status=201).inc()
        REQUEST_LATENCY.labels(method="POST", path="/payments").observe(random.uniform(0.01, 0.3))
        PAYMENT_AMOUNT.observe(random.uniform(10, 5000))
        print(f"  Tick {i+1}: request+payment metric recorded")
    print(f"  Grafana dashboard panels: {[p['title'] for p in GRAFANA_DASHBOARD['panels']]}")
    print(f"  prometheus.yml ready for docker-compose scraping")

    print("\n" + "=" * 60)
    print("EXTENSION D — NDJSON log queries")
    print("=" * 60)
    corr_ids = [str(uuid.uuid4()) for _ in range(4)]
    for i in range(20):
        log.info("request.completed",
                 path=["/payments","/health","/metrics","/payments"][i%4],
                 status=200 if i%7!=0 else 500,
                 latency_ms=round(50+(i*37%500), 2),
                 correlation_id=corr_ids[i%4])
    q = LogQuery()
    print(f"  Total lines: {q.count()}")
    slow = q.where_gt("latency_ms", 200)
    print(f"  latency_ms > 200ms : {slow.count()} hits")
    errs = q.where(status=500)
    print(f"  status=500         : {errs.count()} hits")
    for r in errs.select("path","latency_ms","correlation_id"):
        print(f"    {r}")
    print(f"  NDJSON log → {LOG_FILE.resolve()}")
    print("\n✅ All extensions A–D complete")