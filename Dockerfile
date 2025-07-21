FROM python:3.11-slim

# نصب وابستگی‌های سیستمی
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# نصب Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# نصب ChromeDriver
RUN CHROME_DRIVER_VERSION=$(curl -sS https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE) \
    && wget -O /tmp/chromedriver.zip "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_DRIVER_VERSION}/linux64/chromedriver-linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /tmp \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ \
    && rm -rf /tmp/chromedriver* \
    && chmod +x /usr/local/bin/chromedriver

# تنظیم دایرکتوری کاری
WORKDIR /app

# کپی فایل‌ها
COPY requirements.txt .
COPY main.py .

# نصب وابستگی‌های Python
RUN pip install --no-cache-dir -r requirements.txt

# تنظیم متغیرهای محیطی
ENV DISPLAY=:99
ENV PYTHONUNBUFFERED=1

# باز کردن پورت
EXPOSE 8080

# اجرای برنامه
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "300", "main:app"]
