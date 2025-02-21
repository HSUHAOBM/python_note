# PDF 轉圖片工具 (Docker 版)

這個專案使用 **Docker + Python**，將 PDF 轉換為高解析度的 PNG 圖片。

## 為什麼使用 Docker？

主要是因為 poppler-utils 的安裝與相依性問題。
poppler-utils 是 pdf2image 轉換 PDF 為圖片所必需的工具，但在不同系統上的安裝方式有所不同。
使用 Docker 可以確保環境一致，避免因作業系統差異導致的錯誤。
透過 Docker，只需一次設定，即可在任何環境中快速執行。

## 資料夾結構

```
pdf_to_images/
├── docker-compose.yml  # Docker Compose 設定
├── Dockerfile          # Docker 建置檔案
├── app.py              # PDF 轉圖片主程式
├── input_pdfs/         # 輸入 PDF 資料夾
└── output_images/      # 轉換後的圖片輸出資料夾
```

## 使用方法

### 1. 放入 PDF
將 **要轉換的 PDF** 放入 `input_pdfs/` 目錄。

### 2. 啟動 Docker 容器
進入 `pdf_to_images_docker` 目錄後，執行：

```sh
docker-compose up --build
```

這將會：
- 讀取 `input_pdfs/` 內的 PDF 檔案
- 轉換為 PNG 圖片，輸出到 `output_images/`
