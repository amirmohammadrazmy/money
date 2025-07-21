#!/usr/bin/env bash
set -e

# نصب وابستگی‌های سیستمی لازم
apt-get update && apt-get install -y \
  curl wget ca-certificates fonts-liberation libglib2.0-0 libnss3 libx11-xcb1 \
  libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libpangocairo-1.0-0 \
  libgtk-3-0 xvfb

# نصب بسته‌های Python
pip install --upgrade pip
pip install -r requirements.txt

# نصب Playwright و درایورهای مرورگر
python -m playwright install

# اجرای تست اتصال
echo "=== Running test_connect.py ==="
python test_connect.py || { echo "=== Test failed. Exiting build. ==="; exit 1; }
echo "=== Test passed. Continuing build. ==="
