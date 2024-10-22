from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from Backends import LokiInteraction
import os

app = Flask(__name__)
CORS(app)

# Base application parameters:
@app.route('/')
def homepage():
    service_name = request.args.get('service')
    if service_name:
        services_info = (LokiInteraction.get_service_info(service_name)).to_dict()
        return jsonify({"status" : "OK", "service_info": [service.to_dict() for service in services_info]})
    else:
        services_info = LokiInteraction.get_service_info(None)
        return jsonify({"status" : "OK", "services_info" : [service.to_dict() for service in services_info]})

@app.route('/viewTimelines')
def viewTimelines():
    return render_template('timeline_main_page.html')

@app.route('/getBackendTimeLinesGlobalInfo')
def getBackendTimeLinesGlobalInfo():
    results_for_js = LokiInteraction.getBackendTimeLinesGlobalInfo()
    return jsonify(results_for_js)

# Changes in main.py
if __name__ == '__main__':
    port = int(os.getenv("SWARM_CHECKER_PORT", 8080))
    app.run(host='0.0.0.0', port=port)