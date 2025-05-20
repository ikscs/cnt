from flask import Flask, request, Response
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
#CORS(app, origins=["https://your-frontend-domain.com"])

#from dotenv import load_dotenv
#load_dotenv()

FOLDER = os.environ['DB_FOLDER']

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
