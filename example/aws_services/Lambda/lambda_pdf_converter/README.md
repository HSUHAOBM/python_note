# Lambda PDF 轉換器

這個專案是 AWS Lambda 使用容器映像的前置作業，透過 S3 的觸發，將 S3 的 PDF 檔案轉換為 JPG 圖片，並將結果儲存到新的 S3。

## 前置作業

### AWS CLI 配置

請先安裝並配置 AWS CLI，參考 [AWS CLI 官方文件](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)。

配置 AWS CLI：

```sh
aws configure
```

### 建立 ECR 倉儲

1. 建立 ECR 倉儲

    ```sh
    aws ecr create-repository --repository-name lambda-pdf-converter
    ```

    結果：

    ```
    539247484894.dkr.ecr.ap-northeast-1.amazonaws.com/lambda-pdf-converter
    ```

### Docker

1. 打包 Docker 映像檔

    ```sh
    docker build -t lambda-pdf-converter .
    ```

2. 登入 AWS ECR

    ```sh
    aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 539247484894.dkr.ecr.us-east-1.amazonaws.com
    ```

3. 標記 (tag) & 推送映像檔

    ```sh
    docker tag lambda-pdf-converter:latest 539247484894.dkr.ecr.us-east-1.amazonaws.com/lambda-pdf-converter:latest
    docker push 539247484894.dkr.ecr.us-east-1.amazonaws.com/lambda-pdf-converter:latest
    ```

### Lambda 角色權限

請確保 Lambda 角色具有以下 S3 操作權限：

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::bedrock-poc-20250214-img-pdf-source",
                "arn:aws:s3:::bedrock-poc-20250214-img-pdf-source/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject"
            ],
            "Resource": [
                "arn:aws:s3:::bedrock-poc-20250214-output-jpg",
                "arn:aws:s3:::bedrock-poc-20250214-output-jpg/*"
            ]
        }
    ]
}
```

### Lambda 記憶體及時間設置

根據 PDF 檔案的大小，請適當設置 Lambda 的記憶體和執行時間。建議至少設置 512MB 記憶體和 5 分鐘的超時時間。

```sh
aws lambda update-function-configuration --function-name lambda-pdf-converter --memory-size 512 --timeout 300
```
