import json
import requests
import datetime
import os
import boto3

s3_client = boto3.client("s3")


def lambda_handler(event, context):
    """
    觸發選擇S3事件，將事件通知發送到Slack
    需設置環境參數 slack_webhook_url
    """

    # 取得當前 UTC 時間
    current_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    # 從環境變數讀取 Slack Webhook URL
    slack_webhook_url = os.environ.get("slack_web_url")
    if not slack_webhook_url:
        return {"statusCode": 500, "body": "Slack Webhook URL is missing!"}

    # 解析 S3 事件
    try:
        for record in event["Records"]:
            # 事件名稱，例如 s3:ObjectCreated:Put 或 s3:ObjectRemoved:Delete
            event_name = record["eventName"]
            bucket_name = record["s3"]["bucket"]["name"]  # S3 Bucket 名稱
            file_name = record["s3"]["object"]["key"]  # 檔案名稱

            # 判斷是「上傳」還是「刪除」事件
            if "ObjectCreated" in event_name:
                action = "📂 **新檔案上傳至 S3**"
                file_size = record["s3"]["object"].get(
                    "size", "Unknown")  # 檔案大小
                extra_info = f"📏 **大小**: `{file_size} bytes`"
            elif "ObjectRemoved" in event_name:
                action = "🗑 **檔案已刪除**"
                extra_info = ""
            else:
                continue  # 忽略其他事件

            # 建立 Slack 訊息
            message = {
                "text": f"{action}\n🕒 **時間**: `{current_time} UTC`\n🎯 **Bucket**: `{bucket_name}`\n📄 **檔案**: `{file_name}`\n{extra_info}"
            }

            # 發送通知到 Slack
            response = requests.post(slack_webhook_url, json=message)
            print(f"Slack Response: {response.status_code}, {response.text}")

        return {"statusCode": 200, "body": "Slack notification sent"}
    except Exception as e:
        print(f"Error processing S3 event: {e}")
        return {"statusCode": 500, "body": f"Failed to process S3 event: {str(e)}"}
