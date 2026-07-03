# ── Celery app factory ────────────────────────────────────────────────────────
# Configures the Celery instance with broker, result backend, queue routing,
# and beat schedule. OTel instrumentation is guarded by CELERY_WORKER env var
# so only the worker process (not the FastAPI server) registers its own tracer.

import os
# from celery.schedules import crontab
from src.utils.config import config
from datetime import timedelta
from celery import Celery
from .celery_config import CeleryConfig

from opentelemetry.instrumentation.celery import CeleryInstrumentor
from src.utils.telemetry import setup_telemetry 

bg_task = Celery(
    "celery",
    include=[
        "celery_app.email",
        "celery_app.download",
        "celery_app.orchestrator",
    ],
)

bg_task.conf.update(
    task_always_eager=False,
)
bg_task.conf.broker_connection_retry_on_startup = True

bg_task.config_from_object(CeleryConfig)

# OTel init guarded by env var: celery.py is imported at FastAPI startup too,
# but we only want the worker process to have its own tracer (service_name="flume-worker")
if os.getenv("CELERY_WORKER") == "true":
    setup_telemetry(service_name="flume-worker")
    CeleryInstrumentor().instrument()

# interval = config.celery_beat_interval
bg_task.conf.beat_schedule = {
}

# Schedule,Crontab Code,Description
# Every 2 minutes,crontab(minute='*/2'),"12:00, 12:02, 12:04..."
# Every hour at minute 2,crontab(minute=2),"12:02, 1:02, 2:02..."
# Every 2 hours,"crontab(hour='*/2', minute=0)","12:00, 2:00, 4:00..."
# Specific minutes,"crontab(minute='0,15,30,45')",Every quarter hour