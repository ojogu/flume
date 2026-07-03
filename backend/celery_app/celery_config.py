

from kombu import Queue
from src.utils.config import config


class CeleryConfig:
    """
    Centralized Celery configuration using class-based settings.
    Import this into your Celery app with:
        app.config_from_object('celery_app.celery_config.CeleryConfig')
    """

    # --------------------------
    # Broker Settings
    # --------------------------
    broker_url = config.celery_broker_url
    result_backend = config.celery_result_backend

    # --------------------------
    # Serialization
    # --------------------------
    task_serializer = "json"
    result_serializer = "json"
    accept_content = ["json"]
    timezone = "UTC"
    enable_utc = True

    # --------------------------
    # Queue Definitions
    # --------------------------
    task_default_queue = "default"
    task_queues = (
        Queue("default", routing_key="default"),
        Queue("email", routing_key="email"),
        Queue("orchestrator", routing_key="orchestrator"),
        Queue("op.download", routing_key="op.download"),
    )

    # --------------------------
    # Task Routing
    # --------------------------
    task_routes = {
        "jobs.email.send":         {"queue": "email"},
        "jobs.orchestrator.process": {"queue": "orchestrator"},
        "jobs.download.execute":   {"queue": "op.download"},
    }


    # --------------------------
    # Worker Behavior
    # --------------------------
    worker_prefetch_multiplier = 1
    task_acks_late = True
    worker_max_tasks_per_child = 1000

    # --------------------------
    # Retry Policy
    # --------------------------
    task_default_retry_delay = 60
    task_max_retries = 3

    # --------------------------
    # Beat (Scheduler) Settings
    # --------------------------
    beat_scheduler = "celery.beat.PersistentScheduler"
    beat_schedule_filename = "celerybeat-schedule"

    # --------------------------
    # Logging & Monitoring
    # --------------------------
    worker_hijack_root_logger = False
    worker_log_color = False
    worker_send_task_events = True
    task_send_sent_event = True
    
    # Ensure logging configuration is preserved
    worker_log_format = '[%(asctime)s] [%(levelname)s] %(name)s - %(message)s'
    worker_task_log_format = '[%(asctime)s] [%(levelname)s] %(name)s - %(message)s'



"""

# Start Redis (if using Docker)
docker run -d --name redis -p 6379:6379 redis:alpine

# Or install Redis locally
# Ubuntu: sudo apt-get install redis-server
# macOS: brew install redis

# Install required packages
pip install celery[redis] flower

# Start Celery worker (in one terminal)
celery -A celery_app.celery.bg_task worker -l info -Q default,email

-A celery_app.celery.bg_task → celery_app/celery.py file, bg_task is the Celery() instance you defined

worker → starts a worker

-l info → log level

-Q ... → tell this worker which queues to listen on


# Start Celery Beat scheduler (in another terminal)
celery -A celery_app.celery beat --loglevel=info



# Optional: Start Flower monitoring UI (in third terminal)
celery -A celery_app.celery flower --port=5555

# Production startup (single command)
celery -A src.services.celery_app worker --beat --loglevel=info --detach

# Check task status
celery -A src.services.celery_app inspect active

# Monitor with Flower
# Open browser to http://localhost:5555
"""