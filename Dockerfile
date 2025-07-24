FROM python:3.10-slim

# نصب ابزارها
RUN apt-get update && apt-get install -y \
    curl wget fonts-liberation libglib2.0-0 libnss3 libx11-xcb1 \
    libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libpangocairo-1.0-0 \
    libgtk-3-0 xvfb \
    && apt-get clean

# کپی فایل‌ها
WORKDIR /app
COPY . /app

# نصب پکیج‌ها
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && python -m playwright install

# اجرای اسکریپت ورود
CMD ["python", "entrypoint.py"]
