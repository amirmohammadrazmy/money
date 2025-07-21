FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    curl wget ca-certificates fonts-liberation libglib2.0-0 libnss3 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libpangocairo-1.0-0 libgtk-3-0 xvfb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m playwright install

COPY . .

ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["python", "main.py"]
