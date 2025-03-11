# Chat AI Model

## 1. 專案簡介
這是一個基於 Flask 的 AI 聊天應用，透過 AWS Bedrock 提供 Claude-3 服務。

## 2. AWS 憑證設定
- 用 **掛載 `.aws` 目錄** 方式，設定在 `docker-compose.yml`
- Windows: `C:/Users/你的帳戶/.aws:/root/.aws:ro`
- Linux: `~/.aws:/root/.aws:ro`

## 3. 檔案類型處理
- 圖片檔案(JPG、PNG)：轉換為 Base64 格式，傳送給 AI 分析。
- 文件檔案(PDF、Word、Excel、TXT)：先用 Textract 解析文件內容，然後將提取的文字傳送給 AI 分析。
