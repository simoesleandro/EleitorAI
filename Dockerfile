FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m playwright install chromium --with-deps

COPY . .

RUN mkdir -p data logs

ENV DB_PATH=/data/eleitorai.db
ENV PYTHONUNBUFFERED=1

EXPOSE 5090

CMD ["python", "-m", "app"]
