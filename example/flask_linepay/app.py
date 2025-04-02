import hashlib
import hmac
import base64
import uuid
import json
import requests
import logging
from flask import Flask, request, jsonify, render_template
from config import LINE_PAY_CHANNEL_ID, LINE_PAY_CHANNEL_SECRET, LINE_PAY_API_URL, LINE_PAY_CONFIRM_URL

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def generate_linepay_signature(secret, uri, body, nonce):
    """產生 LINE Pay `X-LINE-Authorization` 簽名"""
    key = bytes(secret, 'utf-8')
    message = (secret + uri + json.dumps(body) + nonce).encode('utf-8')
    signature = hmac.new(key, message, hashlib.sha256).digest()
    return base64.b64encode(signature).decode('utf-8')


def generate_linepay_get_signature(secret, uri, query_string, nonce):
    key = bytes(secret, 'utf-8')
    message = (secret + uri + query_string + nonce).encode('utf-8')
    signature = hmac.new(key, message, hashlib.sha256).digest()
    return base64.b64encode(signature).decode('utf-8')

# 提供前端頁面


@app.route("/")
def index():
    return render_template("index.html")


# 1. 支付請求
@app.route("/pay", methods=["POST"])
def pay():
    try:
        data = request.json or {}
        order_id = data.get(
            "order_id", f"order_{uuid.uuid4().hex[:8]}")  # 自動生成唯一 orderId
        amount = int(data.get("amount", 100))
        product_name = data.get("product_name", "測試商品")  # 從參數取得商品名稱
        product_id = data.get("product_id", "product1")  # 從參數取得商品 ID
        product_quantity = int(data.get("product_quantity", 1))  # 從參數取得商品數量

        # 根據 product_id 設定對應的圖片 URL
        product_image_url = {
            "product1": "https://tw.portal-pokemon.com/play/resources/pokedex/img/pm/6bad448cb0997a928b94e72b67eacb861271f796.png",  # 走路草
            "product2": "https://tw.portal-pokemon.com/play/resources/pokedex/img/pm/441132f5cdf87b0e46f96952f16c2dfc75911054.png",  # 呆呆獸
            "product3": "https://tw.portal-pokemon.com/play/resources/pokedex/img/pm/a42f1e83fdb6809384f2461670a1d81e227df05c.png"   # 卡比獸
        }.get(product_id, "https://example.com/default.png")  # 預設圖片 URL

        # 計算正確的 amount
        calculated_amount = product_quantity * amount

        payload = {
            "amount": calculated_amount,  # 使用計算後的金額
            "currency": "TWD",
            "orderId": order_id,  # 訂單編號
            "packages": [
                {
                    "id": "package1",  # 系列名或分店名
                    "amount": calculated_amount,  # 確保與產品總價一致
                    "name": product_name,  # 商品名稱
                    "products": [
                        {
                            "id": product_id,  # 商品 ID
                            "name": product_name,  # 商品名稱
                            "quantity": product_quantity,  # 商品數量
                            "price": amount,  # 單價
                            "imageUrl": product_image_url,  # 商品圖片 URL
                        }
                    ]
                }
            ],
            "redirectUrls": {
                "confirmUrl": f"{LINE_PAY_CONFIRM_URL}?amount={calculated_amount}",
                "cancelUrl": "http://localhost:5000/cancel"
            }
        }

        nonce = str(uuid.uuid4())
        signature = generate_linepay_signature(
            LINE_PAY_CHANNEL_SECRET, "/v3/payments/request", payload, nonce)

        # 保持原來的 headers 不變
        headers = {
            "Content-Type": "application/json",
            "X-LINE-ChannelId": str(LINE_PAY_CHANNEL_ID),
            "X-LINE-Authorization": signature,
            "X-LINE-Authorization-Nonce": nonce
        }

        logger.info("Request headers: %s", headers)
        logger.info("Request payload: %s", json.dumps(
            payload, indent=2, ensure_ascii=False))

        response = requests.post(
            f"{LINE_PAY_API_URL}/v3/payments/request",
            headers=headers,
            json=payload
        )

        response_data = response.json()
        logger.info("✅ 付款請求回應: %s", json.dumps(
            response_data, indent=2, ensure_ascii=False))

        if response_data.get("returnCode") == "0000":
            return jsonify({"paymentUrl": response_data["info"]["paymentUrl"]["web"]})
        else:
            return jsonify({
                "error": response_data.get("returnMessage"),
                "code": response_data.get("returnCode")
            }), 400

    except Exception as e:
        logger.error("支付請求失敗: %s", str(e))
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


# 2. 處理支付回調
@app.route("/callback")
def callback():
    try:
        transaction_id = request.args.get("transactionId")
        amount = int(request.args.get("amount", 0))  # 從 query string 抓金額

        if not transaction_id:
            return "未提供交易 ID", 400

        return render_template("callback.html", transaction_id=transaction_id, amount=amount)

    except Exception as e:
        logger.error("回調處理失敗: %s", str(e))
        return "伺服器錯誤", 500


# 3. 確認支付
@app.route("/confirm", methods=["POST"])
def confirm_payment():
    try:
        data = request.json or {}
        transaction_id = data.get("transactionId")
        amount = int(data.get("amount", 100))

        if not transaction_id:
            return jsonify({"error": "transactionId is required"}), 400

        uri = f"/v3/payments/{transaction_id}/confirm"
        payload = {
            "amount": amount,
            "currency": "TWD"
        }

        nonce = str(uuid.uuid4())
        signature = generate_linepay_signature(
            LINE_PAY_CHANNEL_SECRET, uri, payload, nonce)

        # 保持原來的 headers 不變
        headers = {
            "Content-Type": "application/json",
            "X-LINE-ChannelId": str(LINE_PAY_CHANNEL_ID),
            "X-LINE-Authorization": signature,
            "X-LINE-Authorization-Nonce": nonce
        }

        logger.info("Confirm request headers: %s", headers)
        logger.info("Confirm request payload: %s", json.dumps(
            payload, indent=2, ensure_ascii=False))

        response = requests.post(
            f"{LINE_PAY_API_URL}{uri}",
            headers=headers,
            json=payload
        )

        response_data = response.json()
        logger.info("✅ 確認支付回應: %s", json.dumps(
            response_data, indent=2, ensure_ascii=False))

        if response_data.get("returnCode") == "0000":
            return jsonify({"message": "Payment confirmed", "transactionId": transaction_id})
        else:
            return jsonify({
                "error": response_data.get("returnMessage"),
                "code": response_data.get("returnCode")
            }), 400

    except Exception as e:
        logger.error("確認支付失敗: %s", str(e))
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


# 4. 查詢支付狀態
@app.route("/details", methods=["GET"])
def payment_details():
    try:
        transaction_id = request.args.get("transactionId")
        if not transaction_id:
            return jsonify({"error": "transactionId is required"}), 400

        uri = "/v3/payments"
        query_string = f"transactionId={transaction_id}"
        nonce = str(uuid.uuid4())

        signature = generate_linepay_get_signature(
            LINE_PAY_CHANNEL_SECRET, uri, query_string, nonce)

        headers = {
            "Content-Type": "application/json",
            "X-LINE-ChannelId": str(LINE_PAY_CHANNEL_ID),
            "X-LINE-Authorization": signature,
            "X-LINE-Authorization-Nonce": nonce
        }

        logger.info("🧾 headers: %s", headers)
        logger.info("🧾 query string: %s", query_string)

        response = requests.get(
            f"{LINE_PAY_API_URL}{uri}",
            headers=headers,
            params={"transactionId": transaction_id}
        )

        response_data = response.json()
        logger.info("✅ 查詢結果: %s", json.dumps(
            response_data, indent=2, ensure_ascii=False))

        if response_data.get("returnCode") == "0000":
            return jsonify(response_data["info"])
        else:
            return jsonify({
                "error": response_data.get("returnMessage"),
                "code": response_data.get("returnCode")
            }), 400

    except Exception as e:
        logger.error("查詢失敗: %s", str(e))
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


# 5. 取消支付
@app.route("/cancel")
def cancel():
    try:
        return jsonify({"message": "支付已取消"})
    except Exception as e:
        logger.error("取消支付失敗: %s", str(e))
        return jsonify({"error": "Internal server error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
