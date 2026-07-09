import json
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from sqlalchemy import inspect as sa_inspect

from src.auth.route import auth_route
from src.route.api import api_key_route
from src.route.job import job_route
from src.route.upload import upload_route
from src.route.webhook import webhook_route
from src.utils.config import Settings
from src.utils.db import engine
from src.utils.exception import register_error_handlers
from src.utils.log import RequestContextMiddleware, configure_structlog, get_logger
from src.utils.redis import setup_redis
from src.utils.telemetry import instrument_fastapi_app, setup_telemetry


logger = get_logger(__name__)


# ── Root FastAPI app ───────────────────────────────────────────────────────────
# Mounts two sub-apps: /v1 (public APIs) and /internal (auth/admin).
# Public API serves job submissions, uploads, and docs.
# Internal API serves authentication and API key management.

public_api = FastAPI(title="Public API", version=Settings.PROJECT_VERSION)

internal_api = FastAPI(
    title="Internal API",
    version=Settings.PROJECT_VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

internal_api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routes per sub-app ────────────────────────────────────────────────────────
# Internal: auth (Google OAuth, magic link) + API key CRUD.
# Public: job submission + file uploads.

internal_api.include_router(auth_route)
internal_api.include_router(api_key_route)


public_api.include_router(job_route)
public_api.include_router(upload_route)
public_api.include_router(webhook_route)


@public_api.get("/root", tags=["health"])
def root():
    return {"message": "FlumeAPI"}


# ── Scalar docs (public only) ────────────────────────────────────────────────

@public_api.get("/scalar", include_in_schema=False)
def scalar_docs():
    return get_scalar_api_reference(
        openapi_url="openapi.json",
        title="Public API",
    )


# ── Error handlers per sub-app ───────────────────────────────────────────────

register_error_handlers(public_api)
register_error_handlers(internal_api)

# ── Telemetry per sub-app ────────────────────────────────────────────────────

instrument_fastapi_app(public_api)
instrument_fastapi_app(internal_api)


# ── OpenAPI export ────────────────────────────────────────────────────────────

def export_openapi_spec() -> None:
    spec = public_api.openapi()
    path = Path(__file__).resolve().parent.parent.parent / "openapi.json"
    path.write_text(json.dumps(spec, indent=2))
    logger.info(f"OpenAPI spec written to {path}")


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def life_span(app: FastAPI):
    configure_structlog()
    await setup_redis()

    logger.info("server is starting...")
    async with engine.begin() as conn:
        tables = await conn.run_sync(lambda c: sa_inspect(c).get_table_names())
        logger.info(f"Tables created: {tables}")

    export_openapi_spec()
    yield


# ── Root app ──────────────────────────────────────────────────────────────────

app = FastAPI(
    lifespan=life_span,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestContextMiddleware)

setup_telemetry()

app.mount("/v1", public_api)
app.mount("/internal", internal_api)
