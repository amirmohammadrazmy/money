# Base image رسمی با node و playwright
FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# تنظیمات محیط
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# نصب وابستگی‌های اضافی اگه خواستی
RUN apt-get update && apt-get install -y \
    curl wget xauth xvfb

# ایجاد دایرکتوری پروژه
WORKDIR /app

# کپی کردن فایل‌های پروژه
COPY . /app/

# نصب پکیج‌های پایتون
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# نصب مرورگرهای Playwright (نکته اصلی!)
RUN playwright install --with-deps

# اجرای تست اتصال
RUN python test_connect.py

# اجرای فایل اصلی در صورت موفقیت
CMD ["python", "main.py"]
