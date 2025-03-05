import boto3
import json

# 初始化 Textract 客戶端
textract = boto3.client("textract", region_name="us-east-1")  # 請替換成你的 AWS 區域

# 讀取本地圖片檔案
image_path = "a.png"  # 替換成你的圖片檔案路徑
with open(image_path, "rb") as image_file:
    image_bytes = image_file.read()

# 呼叫 Textract API 進行 OCR 處理
response = textract.detect_document_text(Document={"Bytes": image_bytes})

# textract_client = boto3.client('textract', region_name="us-east-1")
# response = textract_client.analyze_document(
#     Document={'S3Object': {'Bucket': BUCKET_NAME, 'Name': key}},
#     FeatureTypes=['TABLES', 'FORMS']
# )

# 解析結果
extracted_text = []
for block in response["Blocks"]:
    if block["BlockType"] == "LINE":
        extracted_text.append(block["Text"])

# 儲存 JSON 檔案
output_path = "textract_output.json"
with open(output_path, "w", encoding="utf-8") as json_file:
    json.dump({"extracted_text": extracted_text},
              json_file, ensure_ascii=False, indent=4)

print(f"文字辨識結果已儲存至 {output_path}")
print(f"辨識結果：\n{extracted_text}")
