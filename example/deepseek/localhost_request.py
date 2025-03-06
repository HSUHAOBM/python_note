import requests
import json

# 本地 Ollama 伺服器 API URL
OLLAMA_URL = "http://localhost:11434/api/generate"

# 設定要使用的模型 (cmd ollama list 可查看所有模型)
MODEL_NAME = "deepseek-r1:1.5b"

# 請求數據
payload = {
    "model": MODEL_NAME,
    "prompt": "用 Python 寫一個簡單的 HTTP 伺服器",
    "stream": False
}

# 發送 POST 請求
response = requests.post(OLLAMA_URL, json=payload)

# 解析回應
if response.status_code == 200:
    result = response.json()
    print("Ollama 回應：", result["response"])
else:
    print("請求失敗:", response.status_code, response.text)
