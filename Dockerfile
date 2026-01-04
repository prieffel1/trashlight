FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

CMD ["python", "-u","main.py"]

# This Dockerfile sets up a Python 3.12 slim environment,