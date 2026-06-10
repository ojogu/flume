from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy import inspect as sa_inspect
from src.utils.db import engine
from src.utils.config import Settings
from src.utils.redis import setup_redis
from src.utils.exception import register_error_handlers
from src.utils.telemetry import setup_telemetry
from src.utils.log import RequestContextMiddleware, configure_structlog, get_logger
from fastapi.middleware.cors import CORSMiddleware
from src.auth.route import auth_route
from src.route.api import api_key_route


logger = get_logger(__name__)


@asynccontextmanager
async def life_span(app: FastAPI):
    """
    Lifecycle event handler for the FastAPI application.

    This asynchronous function is called when the FastAPI application starts up
    and shuts down. It initializes the database on startup and performs cleanup
    on shutdown.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: This function yields control back to the application after startup.
    """

    # Run once at import time, to overide uvicorn setup
    configure_structlog()

    #initialize redis 
    await setup_redis()


    logger.info("server is starting....")
    async with engine.begin() as conn:
        tables = await conn.run_sync(lambda c: sa_inspect(c).get_table_names())
        logger.info(f"Tables created: {tables}")

    yield


app = FastAPI(lifespan=life_span)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request context middleware for structlog
app.add_middleware(RequestContextMiddleware)

# setup telemetry
setup_telemetry(app)

# register error handlers
register_error_handlers(app)


app.include_router(auth_route, prefix=Settings.API_V1_PREFIX)
app.include_router(api_key_route, prefix=Settings.API_V1_PREFIX)


@app.get(f"{Settings.API_V1_PREFIX}/root")
def root():
    """
    Root endpoint for the FastAPI application.

    Returns:
        str: A simple greeting message.
    """
    return {"message": "FlumeAPI"}