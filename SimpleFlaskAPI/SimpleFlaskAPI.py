import os
from os import times

from flask import Flask, jsonify, render_template

app = Flask(__name__)
print("*" * 50)
print("Hello from application", end = " ")
print(app)
print("*" * 50)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == "__main__":
    port = int(os.getenv("FLASK_APP_PORT", 8080))
    app.run(host='0.0.0.0', port=port)
