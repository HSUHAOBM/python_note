import json
import boto3
import os


def lambda_handler(event=None, context=None):
    """
        呼叫 AI 模型的範例
    """
    try:
        # 指定區域（如果環境變數未設定）
        region = os.environ.get('AWS_REGION', 'us-east-1')

        # 初始化 Bedrock 客戶端，明確指定區域
        bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)

        # 解析輸入
        message = event.get('message', 'Hello, how are you today?')

        # 準備請求體
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": message
                        }
                    ]
                }
            ]
        }

        # 呼叫模型
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
            body=json.dumps(request_body)
        )

        # 解析響應
        response_body = json.loads(response['body'].read().decode('utf-8'))
        model_response = response_body['content'][0]['text']
        print(f"模型響應: {model_response}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': model_response
            })
        }

    except Exception as e:
        print(f"錯誤: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            })
        }


if __name__ == "__main__":

    lambda_handler(
        event={'message': 'Hello, how are you today?'}, context=None)
