FROM python:3.10-slim

# نصب ابزارهای لازم
RUN apt-get update && apt-get install -y \
    wget curl xvfb fonts-liberation libglib2.0-0 libnss3 libx11-xcb1 \
    libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libpangocairo-1.0-0 \
    libgtk-3-0 --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# نصب پکیج‌های پروژه
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# نصب Playwright و مرورگرها
RUN python -m playwright install

# کپی باقی فایل‌های پروژه
COPY . .

# اجرای فایل اصلی که اتصال رو تست می‌کنه و بعد main.py رو اجرا می‌کنه
CMD ["xvfb-run", "python", "entrypoint.py"]
