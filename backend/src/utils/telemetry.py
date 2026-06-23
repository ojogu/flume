import logging
from fastapi import FastAPI
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor

# ── OpenTelemetry bootstrap ────────────────────────────────────────────────────
# Wires up traces (Tempo), metrics (Prometheus), and logs (Loki) via OTLP to the
# collector. Each sub-app is instrumented separately via instrument_fastapi_app().
# The gRPC endpoint of your OpenTelemetry Collector.
# In Docker Compose, "otel-collector" resolves to the collector container.
# For local dev outside Docker, swap this to "http://localhost:4317".
OTEL_ENDPOINT = "http://otel-collector:4317"


def setup_telemetry(service_name: str = "flume-api"):
    """
    Bootstraps the three OTel signals (traces, metrics, logs) and registers
    them with the global OTel SDK providers. Call this once at application startup.
    All signals are tagged with `service_name` so they're identifiable in
    Grafana / Tempo / Loki / Prometheus.

    Sub-apps must be instrumented separately via `instrument_fastapi_app(app)`.
    """

    resource = Resource.create({SERVICE_NAME: service_name})

    # ── TRACES ────────────────────────────────────────────────────────────────
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(
            OTLPSpanExporter(endpoint=OTEL_ENDPOINT, insecure=True)
        )
    )
    trace.set_tracer_provider(tracer_provider)

    # ── METRICS ───────────────────────────────────────────────────────────────
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=OTEL_ENDPOINT, insecure=True)
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)

    # ── LOGS ──────────────────────────────────────────────────────────────────
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(
            OTLPLogExporter(endpoint=OTEL_ENDPOINT, insecure=True)
        )
    )
    set_logger_provider(logger_provider)

    LoggingInstrumentor().instrument(set_logging_format=True)
    handler = LoggingHandler(logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.DEBUG)

    # ── HTTPX AUTO-INSTRUMENTATION ───────────────────────────────────────────
    HTTPXClientInstrumentor().instrument()


def instrument_fastapi_app(app: FastAPI):
    """
    Instruments a single FastAPI app instance for OpenTelemetry tracing.
    Call this for each sub-app (public_api, internal_api) after creation.
    """
    FastAPIInstrumentor.instrument_app(app)


# Telemetry flow:
# Creates a Resource tagged with the service name (flume-api)
# Wires up TracerProvider → batches spans → exports to OTel Collector via gRPC
# Wires up MeterProvider → periodically reads metrics → exports to Collector
# Wires up LoggerProvider → batches log records → exports to Collector
# Auto-instruments FastAPI (incoming requests) and httpx (outgoing calls) so spans
# appear without manual instrumentation