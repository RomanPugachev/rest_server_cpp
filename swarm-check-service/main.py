from flask import Flask, jsonify, render_template, request
from Backends import LokiInteraction
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app)

# Base application parameters:
@app.route('/viewTimelines')
def homepage():
    service_name = request.args.get('service')
    if service_name:
        services_info = (LokiInteraction.get_service_info(service_name)).to_dict()
        return jsonify({"status" : "OK", "service_info": [service.to_dict() for service in services_info]})
    else:
        services_info = LokiInteraction.get_service_info(None)
        return jsonify({"status" : "OK", "services_info" : [service.to_dict() for service in services_info]})

@app.route('/')
def viewTimelines():
    return render_template('timeline_main_page.html')

@app.route('/getBackendTimeLinesGlobalInfo')
def getBackendTimeLinesGlobalInfo():
    results_for_js = LokiInteraction.getBackendTimeLinesGlobalInfo()
    return jsonify(results_for_js)

@app.route('/get-container-logs', defaults={'path': ''})
@app.route('/get-container-logs/<path:path>')
def get_container_logs():
    container_id = request.path.split('/')[-1]
    if container_id is not None:
        result = subprocess.run(['docker', 'logs', container_id], capture_output=True, text=True)
        logs = result.stdout
        return logs
    else:
        return jsonify({"status": "ERROR", "message": "Container id is not provided"})

if __name__ == '__main__':
    port = os.environ.get("PORT")
    if port is not None:
        app.run(host='0.0.0.0', port=int(port))
    else:
        app.run(debug=True, port=5000)
