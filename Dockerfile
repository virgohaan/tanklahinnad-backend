FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    chromium chromium-driver \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

COPY . .
CMD gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120
