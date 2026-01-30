FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# deps mínimas para newspaper3k
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ make libxml2-dev libxslt1-dev libjpeg-dev zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 5001
CMD ["uvicorn", "app.extractor_service:app", "--host", "0.0.0.0", "--port", "5001"]
