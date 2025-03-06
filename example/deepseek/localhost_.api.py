
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "deepseek-r1:1.5b"


@app.route("/chat", methods=["POST"])
def chat():
    """
    使用post api 與本地 DeepSeek 對話
    """
    data = request.json
    prompt = data.get("prompt", "Hi, how are you?")
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)

    if response.status_code == 200:
        return jsonify({"response": response.json().get("response", "")})
    else:
        return jsonify({"error": response.status_code, "message": response.text})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
