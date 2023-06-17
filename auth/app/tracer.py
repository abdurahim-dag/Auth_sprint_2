from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, Span
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.semconv.resource import ResourceAttributes

from app import config
from flask import request

def configure_tracer() -> None:
    trace.set_tracer_provider(TracerProvider(
        resource=Resource.create({
            ResourceAttributes.SERVICE_NAME: 'Movie',
            ResourceAttributes.SERVICE_NAMESPACE: 'auth',
        })
    ))
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=config.settings.jaeger_agent_host,
                agent_port=config.settings.jaeger_agent_port,
            )
        )
    )
    # Чтобы видеть трейсы в консоли
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


def set_instrument_app(app):

    configure_tracer()

    def request_hook(span: Span, environ):
        if span and span.is_recording():
            request_id = request.headers.get('X-Request-Id')
            span.set_attribute('http.request_id', request_id)

    FlaskInstrumentor().instrument_app(
        app,
        request_hook=request_hook
    )

