import os
from cgitb import reset
from datetime import datetime

import psycopg2
from flask import Flask, request
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
    logging.info("Your application accepted a request on homepage!")
    return render_template('index.html')

@app.route('/container_info')
def container_info():
    logging.info("Your application accepted a request on resource /container_info!")
    global accepted_requests_count, start_time
    accepted_requests_count+=1

    # Collecting data from Docker API
    container_id_api, replica_id, app_version = get_docker_metadata()

    # Collect information into a dictionary
    uptime = datetime.now() - start_time
    uptime_seconds = int(uptime.total_seconds())
    months, seconds = divmod(uptime_seconds, 2592000)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    formatted_uptime = f"{months} month, {days} days, {hours} hours, {seconds} seconds"
    info = {
        'service_container_uptime': formatted_uptime,
        'accepted_requests': accepted_requests_count,
        'container_id': container_id_api,
        'replica_id': replica_id,
        'app_version': app_version
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
    print("Application loaded!")

    # Start the Flask app
    port = int(os.getenv("FLASK_APP_PORT", 8080))
    app.run(host='0.0.0.0', port=port)