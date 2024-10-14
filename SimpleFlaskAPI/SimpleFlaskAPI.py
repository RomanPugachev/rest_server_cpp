import os
import psycopg2
from flask import Flask
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.environment_variables import OTEL_RESOURCE_ATTRIBUTES
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
import logging
import os
from flask import Flask, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def home():
    logging.info("Your application accepted a request!")
    return render_template('index.html')

if __name__ == "__main__":
    if os.environ.get('PYTEST_VERSION'):
        os.environ['OTEL_SDK_DISABLED'] = 'true'
    # Set tracer proovider
    otel_resource_attributes = os.getenv("OTEL_RESOURCE_ATTRIBUTES", "deployment.environment=dev-local,service.name=flask")
    resource = Resource(attributes={k.strip(): v.strip() for k, v in (pair.split('=') for pair in otel_resource_attributes.split(','))})
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer_provider = trace.get_tracer_provider()
    # Set up the exporter
    otlp_exporter = OTLPSpanExporter(endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otlp_collector:4318/"))
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    # Initialize Flask app
    FlaskInstrumentor().instrument_app(app)
    print("*" * 50)
    print("Hello from application", end = " ")
    print(app)
    print("*" * 50)
    # Start the Flask app
    port = int(os.getenv("FLASK_APP_PORT", 8080))
    app.run(host='0.0.0.0', port=port)