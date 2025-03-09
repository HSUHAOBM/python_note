from flask import Flask, request, jsonify, render_template
import boto3
import json
import os
import base64
import datetime
import textract
import logging
import tempfile

app = Flask(__name__)

# 初始化 AWS 客戶端
bedrock_client = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1",
    config=boto3.session.Config(
        read_timeout=300,  # 增加讀取超時為 300 秒
        connect_timeout=30  # 增加連線超時為 30 秒
    )
)

# 設置日誌記錄，確保繁體中文顯示正常
log_file = 'app.log'
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
log_handler = logging.FileHandler(log_file, encoding='utf-8')
log_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
logging.getLogger().addHandler(log_handler)


@app.route('/')
def index():
    # 渲染首頁模板
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    # 從前端獲取參數
    model_id = request.form.get('model')
    conversation_and_prompt = request.form.get('conversation_and_prompt')
    max_tokens = int(request.form.get('max_tokens'))
    temperature = float(request.form.get('temperature'))
    top_p = float(request.form.get('top_p'))
    file = request.files.get('file')
    client_ip = request.remote_addr

    logging.info(
        f"收到來自 IP: {client_ip} 的請求，模型 ID: {model_id}，對話與提示詞: {conversation_and_prompt}，Max Tokens: {max_tokens}，Temperature: {temperature}，Top P: {top_p}")

    content = []

    # 如果有上傳文件，處理文件內容
    if file:
        file_content = file.read()
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension in ['.jpg', '.jpeg', '.png']:
            media_type = "image/jpeg" if file_extension in [
                '.jpg', '.jpeg'] else "image/png"
            base64_data = base64.b64encode(file_content).decode('utf-8')
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": base64_data
                }
            })
            logging.info(f"上傳的文件: {file.filename}，媒體類型: {media_type}")
        elif file_extension in ['.doc', '.docx', '.pdf', '.txt', '.xls', '.xlsx']:
            # 使用 textract 解析文件內容
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            text = textract.process(
                temp_file_path, input_encoding='utf-8').decode('utf-8')
            os.remove(temp_file_path)
            content.append({
                "type": "text",
                "text": text
            })
            # 只打印前100個字符
            logging.info(f"上傳的文件: {file.filename}，提取的文本: {text[:100]}...")
        else:
            logging.error(f"不支持的文件類型: {file.filename}")
            return jsonify({"error": "Unsupported file type"})

    # 添加對話與提示詞到 content 中
    content.append({
        "type": "text",
        "text": conversation_and_prompt
    })
    logging.info("已添加對話與提示詞到內容中")

    # 構建請求體
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ]
    }
    logging.info("請求體已構建")

    try:
        # 調用 Bedrock 模型
        response = bedrock_client.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )
        # 解析模型回應
        result = json.loads(response["body"].read().decode("utf-8"))
        output_text = result["content"][0]["text"]
        logging.info("模型回應已接收")
        logging.info(f"模型輸出: {output_text}")
        return jsonify({"response": output_text})
    except Exception as e:
        logging.error(f"調用模型時出錯: {e}")
        return jsonify({"error": str(e)})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
