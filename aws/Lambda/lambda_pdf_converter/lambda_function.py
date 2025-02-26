import boto3
import io
import urllib.parse
from pdf2image import convert_from_bytes

s3 = boto3.client('s3')

# 來源與輸出的 s3 bucket
SOURCE_BUCKET = "bedrock-poc-20250214-img-pdf-source"
DEST_BUCKET = "bedrock-poc-20250214-output-jpg"


def lambda_handler(event, context):
    """
    Lambda 監聽 S3 事件，將 PDF 轉換為 JPG
    """
    print("收到的事件: ", event)

    for record in event['Records']:
        encoded_s3_key = record['s3']['object']['key']
        s3_key = urllib.parse.unquote(encoded_s3_key)

        print(f"處理 PDF: {s3_key}")

        try:
            # 下載 PDF
            pdf_obj = s3.get_object(Bucket=SOURCE_BUCKET, Key=s3_key)
            pdf_bytes = pdf_obj['Body'].read()

            # 轉換 PDF 為圖片
            images = convert_from_bytes(pdf_bytes, dpi=300)

            # 儲存圖片到 S3
            for idx, img in enumerate(images):
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                img_byte_arr.seek(0)

                output_key = f"{s3_key.replace('.pdf', '')}_page_{idx + 1}.jpg"
                s3.put_object(
                    Bucket=DEST_BUCKET,
                    Key=output_key,
                    Body=img_byte_arr,
                    ContentType="image/jpeg"
                )

                print(f"已上傳圖片: {output_key}")

            print(f"完成 PDF 轉換: {s3_key}")

        except Exception as e:
            print(f"錯誤: {str(e)}")

    return {"statusCode": 200, "body": "PDF 轉換成功"}
