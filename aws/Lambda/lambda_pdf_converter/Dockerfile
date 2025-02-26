# 使用 AWS Lambda 官方 Python 3.9 基底映像
FROM public.ecr.aws/lambda/python:3.9

RUN yum install -y gcc gcc-c++ make poppler-utils && \
    pip install --no-cache-dir pdf2image Pillow PyMuPDF boto3

COPY lambda_function.py ./

# 設定 Lambda 進入點
CMD ["lambda_function.lambda_handler"]
