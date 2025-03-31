FROM python:3.9
WORKDIR /app
COPY . /app/
ENV PYTHONUNBUFFERED 1
RUN pip install -r requirements.txt

# 設定 Flask 運行
# CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
CMD ["python", "app.py"]
