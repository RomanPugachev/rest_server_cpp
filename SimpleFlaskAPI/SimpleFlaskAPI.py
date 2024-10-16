import os
from datetime import datetime

import psycopg2
from flask import Flask
import time
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

from Utils import get_docker_metadata

app = Flask(__name__)

start_time = datetime.now()
accepted_requests_count = 0

@app.route('/')
def home():
    logging.info("Your application accepted a request!")
    return render_template('index.html')

@app.route('/container_info')
def container_info():
    global accepted_requests_count, start_time
    accepted_requests_count+=1
    # Read container ID from /proc/self/cgroup (works inside Docker containers)
    try:
        with open('/proc/self/cgroup', 'r') as f:
            lines = f.readlines()
            container_id = lines[-1].strip().split('/')[-1]
    except Exception as e:
        container_id = 'Unknown'

    # Replica ID and version would need to be passed or queried using Docker's API
    replica_id = 'Unknown'  # Placeholder for now
    app_version = '1.0.0'  # You can set this manually or fetch dynamically

    container_id_api, replica_id, app_version = get_docker_metadata()
    # Collect information into a dictionary
    info = {
        'service_container_uptime' : datetime.now() - start_time,
        'accepted_requests': accepted_requests_count,
        'container_id': container_id,
        'replica_id': replica_id,
        'app_version': app_version,
    }
    return jsonify(info)


if __name__ == "__main__":
    if os.environ.get('PYTEST_VERSION'):
        os.environ['OTEL_SDK_DISABLED'] = 'true'

    # Set tracer proovider
    otel_resource_attributes = os.getenv("OTEL_RESOURCE_ATTRIBUTES", "deployment.environment=dev-local,service.name=flask")
    resource = Resource(attributes={k.strip(): v.strip() for k, v in (pair.split('=') for pair in otel_resource_attributes.split(','))})
    trace.set_tracer_provider(TracerProvider(resource=resource))
    tracer_provider = trace.get_tracer_provider()
    # Set up the exporter

    otlp_exporter = OTLPSpanExporter(endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otlp_collector:4318/v1/traces"))
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)

    # Initialize Flask app
    FlaskInstrumentor().instrument_app(app)
    print("*" * 50)
    print("Hello from application", end = " ")
    print(app)
    print("*" * 50)

    # Imitate loading process
    print("Loading application...")
    for i in range(10, 0, -1):
        print(f"Starting in {i} seconds...")
        time.sleep(1)
    print("Application loaded!")

    # Start the Flask app
    port = int(os.getenv("FLASK_APP_PORT", 8080))
    app.run(host='0.0.0.0', port=port)