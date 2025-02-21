# 使用 Python 3.10 Slim 版本，較小巧
FROM python:3.10-slim

# 設定工作目錄
WORKDIR /app

# 安裝必要的系統工具 (包含 poppler-utils)
RUN apt-get update && apt-get install -y poppler-utils && rm -rf /var/lib/apt/lists/*

# 複製 requirements.txt 並安裝 Python 套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY app.py .

# 確保 input_pdfs 和 output_images 目錄存在
RUN mkdir -p /app/input_pdfs /app/output_images

# 預設執行指令
CMD ["python", "app.py"]
