FROM python:3.11-slim

WORKDIR /app

# نصب ابزارهای لازم
RUN apt-get update && apt-get install -y \
    wget curl ca-certificates gnupg \
    libglib2.0-0 libnss3 libx11-xcb1 \
    libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
    libasound2 libpangocairo-1.0-0 libgtk-3-0 \
    xvfb xauth \
 && rm -rf /var/lib/apt/lists/*

# نصب وابستگی‌های Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# نصب playwright و تمام وابستگی‌ها با مرورگرها
RUN pip install playwright && playwright install --with-deps

# کپی فایل‌ها
COPY . .

# اجرای برنامه
ENTRYPOINT ["python", "entrypoint.py"]
