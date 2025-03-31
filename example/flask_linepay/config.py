import os
from dotenv import load_dotenv

# 載入 .env 檔案
load_dotenv()

# 讀取環境變數
LINE_PAY_CHANNEL_ID = os.getenv("LINE_PAY_CHANNEL_ID")
LINE_PAY_CHANNEL_SECRET = os.getenv("LINE_PAY_CHANNEL_SECRET")
LINE_PAY_CONFIRM_URL = os.getenv("LINE_PAY_CONFIRM_URL")
LINE_PAY_API_URL = "https://sandbox-api-pay.line.me"
