FROM node:18-slim

RUN apt-get update && apt-get install -y \
  wget \
  ca-certificates \
  fonts-liberation \
  libappindicator1 \
  libasound2 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libgtk-3-0 \
  libxss1 \
  libnspr4 \
  libnss3 \
  libx11-xcb1 \
  libxcomposite1 \
  libxdamage1 \
  libxrandr2 \
  libgbm1 \
  chromium \
  --no-install-recommends \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

COPY package*.json ./
RUN npm install
COPY . .

CMD ["npm", "start"]
