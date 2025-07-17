from flask import Flask, request, Response
from flask_cors import CORS
from a2wsgi import WSGIMiddleware
import os
import subprocess
import shutil

app = Flask(__name__)
CORS(app)
asgi_app = WSGIMiddleware(app)

#from dotenv import load_dotenv
#load_dotenv()

FOLDER = os.environ['DB_FOLDER']

def safe_run(cmd):
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        status = 200
        txt = result.stdout
    except Exception as err:
        status = 500
        txt = err.stderr
    return status, txt

@app.route("/", methods=["GET"])
def hello():
    status = 200
    try:
        total, used, free = shutil.disk_usage(FOLDER)
        if free < 50 * 1024 * 1024:
            txt = 'Low disk space'
        else:
            txt = f'healthy Total: {total}, Used: {used}, Free: {free}'
    except Exception as err:
        status = 500
        txt = str(err)
    return Response(txt, status = status)

@app.route("/set/<key>", methods=["POST"])
def set_binary(key):
    binary_data = request.data
    if not binary_data:
        return Response("No binary data provided", status=400)

    try:
        with open(f'{FOLDER}/{key}', 'wb') as file:
            file.write(binary_data)
    except Exception as err:
        return Response("Error data save", status=500)

    return Response(f"Binary data stored under key: {key}", status=200)

@app.route("/get/<key>", methods=["GET"])
def get_binary(key):
    try:
        with open(f'{FOLDER}/{key}', 'rb') as file:
            data = file.read()
    except Exception as err:
        data = None

    if data is None:
        return Response("Key not found", status=404)
    return Response(data, content_type="application/octet-stream")

@app.route("/del/<key>", methods=["GET"])
def del_binary(key):
    try:
        os.remove(f'{FOLDER}/{key}')
    except Exception as err:
        return Response("Key not found", status=404)

    return Response(f"Removed: {key}", status=200)

@app.route("/erase", methods=["POST"])
def erase_binary():
    size = request.form['size']
    days = request.form['days']

    cmd = f'/app/eraser.py {size} {days}'
    status, result = safe_run(cmd)

    return Response(result, status=status)

@app.route("/cleanup", methods=["POST"])
def cleanup_storage():
    size = request.form['size']

    cmd = f'/app/cleanup.py {size}'
    status, result = safe_run(cmd)

    return Response(result, status=status)

@app.route("/img/<key>", methods=["GET"])
def get_img(key):
    key = key.split('.')[0]
    try:
        with open(f'{FOLDER}/{key}', 'rb') as file:
            data = file.read()
    except Exception as err:
        data = None

    if data is None:
        return Response("not found", status=404)
    return Response(data, content_type="image/jpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
