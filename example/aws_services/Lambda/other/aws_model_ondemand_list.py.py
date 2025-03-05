import boto3
import json


def main():
    """
    列出支援 ON_DEMAND 推論類型的模型
    可在 Lambda 使用的模型列表
    """

    # 建立 Bedrock client (請自行指定 region)
    bedrock_client = boto3.client('bedrock', region_name='us-east-1')

    # 呼叫 API 列出所有模型
    response = bedrock_client.list_foundation_models()

    # 篩選出支援 ON_DEMAND 的模型
    on_demand_models = []
    for model_summary in response.get('modelSummaries', []):
        inference_types = model_summary.get('inferenceTypesSupported', [])
        if 'ON_DEMAND' in inference_types:
            on_demand_models.append(model_summary)

    print("==== Models with ON_DEMAND inference type ====")
    for model in on_demand_models:
        model_id = model.get('modelId')
        print(
            f"Model ID: {model_id}, Inference Types: {model.get('inferenceTypesSupported')}")

    # 另將結果存成 JSON 檔
    with open("on_demand_models.json", "w", encoding="utf-8") as f:
        json.dump(on_demand_models, f, ensure_ascii=False, indent=2)

    print("\n篩選結果已存到 on_demand_models.json")


if __name__ == "__main__":
    main()
