import os
from flask import Flask
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
import logging
import os
from flask import Flask, jsonify, render_template

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if os.environ.get('PYTEST_VERSION'):
    os.environ['OTEL_SDK_DISABLED'] = 'true'

trace.set_tracer_provider(TracerProvider())
tracer_provider = trace.get_tracer_provider()
otlp_exporter = OTLPSpanExporter()
span_processor = BatchSpanProcessor(otlp_exporter)
tracer_provider.add_span_processor(span_processor)
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
print("*" * 50)
print("Hello from application", end = " ")
print(app)
print("*" * 50)

@app.route('/')
def home():
    logging.info("Your application accepted a request!")
    return render_template('index.html')

if __name__ == "__main__":
    port = int(os.getenv("FLASK_APP_PORT", 8080))
    app.run(host='0.0.0.0', port=port)
