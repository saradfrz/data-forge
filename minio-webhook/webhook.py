import json
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

LAMBDA_URL = "http://lambda:9010/2015-03-31/functions/function/invocations"  # Adjust if Lambda is on a different port

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    data = request.json
    app.logger.info(f"Received event from MinIO: {json.dumps(data, indent=2)}")

    # Forward to Lambda
    try:
        response = requests.post(LAMBDA_URL, json=data)
        response.raise_for_status()
        return jsonify({"status": "forwarded", "lambda_response": response.json()}), 200
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error forwarding event to Lambda: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
