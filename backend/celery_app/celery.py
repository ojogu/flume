# ── Celery app factory ────────────────────────────────────────────────────────
# Configures the Celery instance with broker, result backend, queue routing,and beat schedule. OTel instrumentation runs in each worker process via worker_process_init signal (after fork), not at module import time.

from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_process_init, worker_process_shutdown
from opentelemetry.instrumentation.celery import CeleryInstrumentor

from src.utils.telemetry import setup_telemetry

from .celery_config import CeleryConfig

bg_task = Celery(
    "celery",
    include=[
        "celery_app.email",
        "celery_app.download",
        "celery_app.orchestrator",
        "celery_app.webhook",
        "celery_app.operations",
        "celery_app.cleanup",
    ],
)

bg_task.conf.update(
    task_always_eager=False,
)
bg_task.conf.broker_connection_retry_on_startup = True

bg_task.config_from_object(CeleryConfig)


# interval = config.celery_beat_interval
bg_task.conf.beat_schedule = {
    "cleanup-stale-workspaces": {
        "task": "celery_app.cleanup_stale_workspaces",
        "schedule": crontab(minute="*/2"),
    },
}

# Schedule,Crontab Code,Description
# Every 2 minutes,crontab(minute='*/2'),"12:00, 12:02, 12:04..."
# Every hour at minute 2,crontab(minute=2),"12:02, 1:02, 2:02..."
# Every 2 hours,"crontab(hour='*/2', minute=0)","12:00, 2:00, 4:00..."
# Specific minutes,"crontab(minute='0,15,30,45')",Every quarter hour


@worker_process_init.connect
def on_worker_process_init(**_kwargs):
    setup_telemetry(service_name="flume-worker")
    from src.utils.log import configure_structlog
    configure_structlog()
    CeleryInstrumentor().instrument()


@worker_process_shutdown.connect
def on_worker_process_shutdown(**_kwargs):
    from opentelemetry import metrics, trace
    metrics.get_meter_provider().shutdown()
    trace.get_tracer_provider().shutdown()