import boto3
import json
import urllib.parse
from botocore.exceptions import ClientError
import re
import os
import base64
import time
import datetime

# 初始化 AWS 客戶端，增加超時設置
bedrock_client = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1",
    config=boto3.session.Config(
        read_timeout=300,  # 增加讀取超時為 300 秒
        connect_timeout=30  # 增加連線超時為 30 秒
    )
)
s3_client = boto3.client('s3')

# S3 儲存桶名稱
BUCKET_NAME = "66631.images2model2txtorjson"


def get_presigned_url(bucket, key, expiration=3600):
    """生成 S3 物件的預簽名 URL（備用，僅用於參考）"""
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=expiration
        )
        return url
    except ClientError as e:
        print(f"Error generating presigned URL for {key}: {e}")
        return None


def get_image_data(bucket, key):
    """從 S3 下載圖片並轉換為 Base64 編碼"""
    start_time = time.time()  # 記錄開始時間

    try:
        decoded_key = urllib.parse.unquote(key)
        head_response = s3_client.head_object(Bucket=bucket, Key=decoded_key)
        if head_response['ContentLength'] > 5 * 1024 * 1024:  # 5MB 限制
            raise Exception(f"Image {decoded_key} exceeds 5MB limit")

        response = s3_client.get_object(Bucket=bucket, Key=decoded_key)
        image_data = response['Body'].read()

        file_extension = os.path.splitext(decoded_key)[1].lower()
        media_type = "image/jpeg" if file_extension in [
            '.jpg', '.jpeg'] else "image/png"

        base64_data = base64.b64encode(image_data).decode('utf-8')

        end_time = time.time()  # 記錄結束時間
        print(
            f"Step: Get image data from S3 and encode to Base64, Time: {end_time - start_time:.3f} seconds")
        return base64_data, media_type
    except ClientError as e:
        print(f"Error getting image data for {key}: {e}")
        return None, None


def process_image(bucket, key):
    """處理圖片，提取公司信息和員工名單數據並生成 JSON 摘要"""
    decoded_key = urllib.parse.unquote(key)
    print(f"Processing file: s3://{bucket}/{decoded_key}")

    # Step 1: 獲取圖片數據
    step1_start = time.time()
    base64_image_data, media_type = get_image_data(bucket, decoded_key)
    step1_end = time.time()
    if not base64_image_data:
        raise Exception(f"Failed to get Base64 image data for {decoded_key}")
    print(
        f"Step: Total time for fetching image data, Time: {step1_end - step1_start:.3f} seconds")

    # Step 2: 構建請求體
    step2_start = time.time()
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "temperature": 0.2,
        "top_p": 0.6,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": base64_image_data
                        }
                    },
                    {
                        "type": "text",
                        "text": """
                            請解析這張通訊錄圖片，並輸出純 JSON 格式：
                            - 「部門 department」需正確提取，僅包含部門名稱，不含職位，例如「財務部」而非「財務部經理」。
                            - 「姓名 name」、「分機號碼」不得省略，若無則填入 ""。
                            - 「分機號碼 extension」格式標準化，移除多餘空格。
                            - 按表格順序從左至右、從上到下解析部門、職位、姓名和分機號碼。

                            輸出格式：
                            {
                                "company": {
                                    "name": "公司名稱（中英文對照）",
                                    "address": "公司地址",
                                    "phone": "公司電話"
                                },
                                "employees": [
                                    {
                                        "department": "部門名稱（中英文對照）",
                                        "name": "姓名（中文 / 英文）",
                                        "position": "職位（中英文對照）",
                                        "extension": "分機號碼"
                                    }
                                ]
                            }
                        """
                    }
                ]
            }
        ]
    }
    step2_end = time.time()
    print(
        f"Step: Build request body for Bedrock, Time: {step2_end - step2_start:.3f} seconds")

    try:
        # Step 3: 調用 Bedrock 模型
        step3_start = time.time()
        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            contentType="application/json",
            accept="application/json",
            body=json.dumps(request_body)
        )
        step3_end = time.time()
        print(
            f"Step: Invoke Bedrock model, Time: {step3_end - step3_start:.3f} seconds")

        # Step 4: 解析回應
        step4_start = time.time()
        result = json.loads(response["body"].read().decode("utf-8"))
        output_text = result["content"][0]["text"]
        print("Model response:", output_text)

        try:
            data = json.loads(output_text)
            company = data.get("company", {})
            employees = data.get("employees", [])
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response: {e}")
            # 嘗試清理並修復回應
            cleaned_text = re.sub(
                r'^.*?(?={)', '', output_text, flags=re.DOTALL)  # 移除前置文字直到 JSON 開始
            cleaned_text = re.sub(
                r'}.*?$', '}', cleaned_text, flags=re.DOTALL)     # 確保結束符正確
            cleaned_text = cleaned_text.strip()
            try:
                data = json.loads(cleaned_text)
                company = data.get("company", {})
                employees = data.get("employees", [])
            except json.JSONDecodeError as e2:
                # 儲存原始回應以供檢查
                s3_client.put_object(
                    Bucket=bucket,
                    Key=f"debug/{os.path.splitext(decoded_key)[0]}_raw_response.txt",
                    Body=output_text.encode("utf-8"),
                    ContentType="text/plain"
                )
                print(f"Failed to clean and decode JSON: {e2}")
                company = {}
                employees = []
        step4_end = time.time()
        print(
            f"Step: Parse Bedrock response, Time: {step4_end - step4_start:.3f} seconds")

        # Step 5: 清理數據
        step5_start = time.time()
        cleaned_employees = []
        for emp in employees:
            cleaned_emp = {
                "department": emp.get("department", "").strip(),
                "name": emp.get("name", "").strip(),
                "position": emp.get("position", "").strip(),
                # 清除空格
                "extension": re.sub(r"\s+", "", emp.get("extension", "").strip())
            }
            # 只要有任一欄位有值，就保留這筆記錄（允許 name 為空）
            if any(cleaned_emp.values()):
                cleaned_employees.append(cleaned_emp)

        # 清理公司數據
        cleaned_company = {
            "name": company.get("name", "").strip(),
            "address": company.get("address", "").strip(),
            "phone": company.get("phone", "").strip()
        }

        if not cleaned_employees:
            print(f"No valid employees extracted from {decoded_key}")
            return

        # 組合最終 JSON
        final_data = {
            "company": cleaned_company,
            "employees": cleaned_employees
        }
        step5_end = time.time()
        print(
            f"Step: Clean and validate data, Time: {step5_end - step5_start:.3f} seconds")

        # Step 6: 儲存結果到 S3
        step6_start = time.time()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        base_name = os.path.splitext(os.path.basename(decoded_key))[0]
        output_key = f"result_text/{base_name}_{timestamp}_summary.json"

        s3_client.put_object(
            Bucket=bucket,
            Key=output_key,
            Body=json.dumps(final_data, ensure_ascii=False).encode("utf-8"),
            ContentType="application/json"
        )
        step6_end = time.time()
        print(
            f"Step: Upload result to S3, Time: {step6_end - step6_start:.3f} seconds")

        print(f"OCR result uploaded to s3://{bucket}/{output_key}")
        return cleaned_employees

    except Exception as e:
        print(f"Error processing {decoded_key}: {e}")
        return []


def lambda_handler(event, context):
    """
    Lambda 入口函數，處理 S3 事件觸發
    將通訊錄圖片透過 AI model，轉換為 JSON 格式
    """
    total_start = time.time()  # 整體開始時間
    all_employees = []
    for record in event.get('Records', []):
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        employees = process_image(bucket, key)
        if employees:
            all_employees.extend(employees)

    total_end = time.time()
    print(
        f"Total processing time for all records: {total_end - total_start:.3f} seconds")

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Processing completed', 'employee_count': len(all_employees)})
    }


if __name__ == "__main__":
    test_event = {
        "Records": [{
            "s3": {
                "bucket": {"name": BUCKET_NAME},
                "object": {"key": "images/皇家酒店通訊錄202502_page_1.jpg"}
            }
        }]
    }
    lambda_handler(test_event, None)
