from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.utils.db import init_db
from src.utils.config import Settings
from src.utils.exception import register_error_handlers
from src.utils.telemetry import setup_telemetry
from src.utils.log import RequestContextMiddleware, configure_structlog
from fastapi.middleware.cors import CORSMiddleware
from src.route.auth import auth_route


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

    # Startup: Initialize the database
    print(f"server is starting....")
    await init_db()
    print(f"server has started!!")

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


@app.get(f"{Settings.API_V1_PREFIX}/root")
def root():
    """
    Root endpoint for the FastAPI application.

    Returns:
        str: A simple greeting message.
    """
    return {"message": "FlumeAPI"}