import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
from flask import Flask, render_template_string, jsonify
import threading
import json
from datetime import datetime

# تنظیمات لاگینگ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# تنظیمات سایت
LOGIN_URL = "https://2ad.ir/auth/signin"
LINKS_PAGE_URL = "https://2ad.ir/member/links"
USERNAME = "behtarinarts@gmail.com"
PASSWORD = "amir1384328"

# فایل‌های لینک در GitHub
GITHUB_FILES = [
    "https://raw.githubusercontent.com/amirmohammadrazmy/money/download_links_480p.txt",
    "https://raw.githubusercontent.com/amirmohammadrazmy/money/output_links.txt"
]

app = Flask(__name__)

class LinkShortener:
    def __init__(self):
        self.driver = None
        self.shortened_links = []
        self.failed_links = []
        self.current_index = 0
        self.total_links = 0
        self.is_running = False
        self.status = "آماده"
        
    def setup_driver(self):
        """راه‌اندازی Chrome WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            logger.info("WebDriver راه‌اندازی شد")
            return True
        except Exception as e:
            logger.error(f"خطا در راه‌اندازی WebDriver: {e}")
            return False
    
    def login(self):
        """ورود به سایت"""
        try:
            logger.info("شروع فرآیند ورود...")
            self.driver.get(LOGIN_URL)
            
            # انتظار برای بارگذاری صفحه
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            
            # وارد کردن نام کاربری
            username_field = self.driver.find_element(By.NAME, "username")
            username_field.clear()
            username_field.send_keys(USERNAME)
            
            # وارد کردن رمز عبور
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(PASSWORD)
            
            # کلیک روی دکمه ورود
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button.submit-button")
            login_button.click()
            
            # انتظار برای ورود موفق
            time.sleep(3)
            
            # بررسی ورود موفق
            if "member" in self.driver.current_url or "dashboard" in self.driver.current_url:
                logger.info("ورود موفقیت‌آمیز بود")
                return True
            else:
                logger.error("ورود ناموفق")
                return False
                
        except Exception as e:
            logger.error(f"خطا در فرآیند ورود: {e}")
            return False
    
    def go_to_links_page(self):
        """رفتن به صفحه لینک‌ها"""
        try:
            self.driver.get(LINKS_PAGE_URL)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "modal-open-new-link"))
            )
            logger.info("وارد صفحه لینک‌ها شدیم")
            return True
        except Exception as e:
            logger.error(f"خطا در رفتن به صفحه لینک‌ها: {e}")
            return False
    
    def shorten_single_link(self, url):
        """کوتاه کردن یک لینک"""
        try:
            # کلیک روی دکمه لینک جدید
            new_link_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "modal-open-new-link"))
            )
            new_link_button.click()
            
            # انتظار برای باز شدن فرم
            url_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "url"))
            )
            
            # پاک کردن فیلد و وارد کردن URL جدید
            url_input.clear()
            url_input.send_keys(url.strip())
            
            # کلیک روی دکمه کوتاه کن
            shorten_button = self.driver.find_element(By.XPATH, "//span[text()='کوتاه کن']")
            shorten_button.click()
            
            # انتظار برای نتیجه
            result_input = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "link-result-url"))
            )
            
            # گرفتن لینک کوتاه شده
            shortened_url = result_input.get_attribute("value")
            
            if shortened_url:
                # باز کردن لینک در تب جدید
                self.driver.execute_script(f"window.open('{shortened_url}', '_blank');")
                time.sleep(2)
                
                # برگشت به تب اصلی
                self.driver.switch_to.window(self.driver.window_handles[0])
                
                logger.info(f"لینک کوتاه شد: {url} -> {shortened_url}")
                return shortened_url
            else:
                logger.error(f"لینک کوتاه نشد: {url}")
                return None
                
        except Exception as e:
            logger.error(f"خطا در کوتاه کردن لینک {url}: {e}")
            return None
    
    def load_links_from_github(self):
        """بارگذاری لینک‌ها از فایل‌های GitHub"""
        all_links = []
        
        for file_url in GITHUB_FILES:
            try:
                logger.info(f"بارگذاری لینک‌ها از: {file_url}")
                response = requests.get(file_url, timeout=10)
                response.raise_for_status()
                
                links = [link.strip() for link in response.text.split('\n') if link.strip()]
                all_links.extend(links)
                logger.info(f"{len(links)} لینک از این فایل بارگذاری شد")
                
            except Exception as e:
                logger.error(f"خطا در بارگذاری فایل {file_url}: {e}")
        
        logger.info(f"مجموع {len(all_links)} لینک بارگذاری شد")
        return all_links
    
    def run_shortening_process(self):
        """اجرای فرآیند کوتاه کردن لینک‌ها"""
        self.is_running = True
        self.status = "در حال اجرا..."
        
        try:
            # راه‌اندازی درایور
            self.status = "راه‌اندازی مرورگر..."
            if not self.setup_driver():
                self.status = "خطا در راه‌اندازی مرورگر"
                return
            
            # ورود به سایت
            self.status = "ورود به سایت..."
            if not self.login():
                self.status = "خطا در ورود به سایت"
                return
            
            # رفتن به صفحه لینک‌ها
            self.status = "رفتن به صفحه لینک‌ها..."
            if not self.go_to_links_page():
                self.status = "خطا در رفتن به صفحه لینک‌ها"
                return
            
            # بارگذاری لینک‌ها
            self.status = "بارگذاری لینک‌ها..."
            links = self.load_links_from_github()
            
            if not links:
                self.status = "هیچ لینکی یافت نشد"
                return
            
            self.total_links = len(links)
            self.status = f"شروع کوتاه کردن {self.total_links} لینک..."
            
            # کوتاه کردن لینک‌ها
            for i, link in enumerate(links):
                if not self.is_running:
                    break
                
                self.current_index = i + 1
                self.status = f"پردازش لینک {self.current_index} از {self.total_links}"
                
                shortened = self.shorten_single_link(link)
                
                if shortened:
                    self.shortened_links.append({
                        'original': link,
                        'shortened': shortened,
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    self.failed_links.append({
                        'url': link,
                        'error': 'کوتاه نشد',
                        'timestamp': datetime.now().isoformat()
                    })
                
                # وقفه بین درخواست‌ها
                time.sleep(2)
            
            self.status = f"تمام شد! {len(self.shortened_links)} لینک موفق، {len(self.failed_links)} ناموفق"
            
        except Exception as e:
            self.status = f"خطای عمومی: {str(e)}"
            logger.error(f"خطای عمومی: {e}")
        
        finally:
            if self.driver:
                self.driver.quit()
            self.is_running = False

# ایجاد instance از کلاس
shortener = LinkShortener()

@app.route('/')
def index():
    """صفحه اصلی"""
    html = """
    <!DOCTYPE html>
    <html dir="rtl" lang="fa">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>کوتاه کننده لینک 2AD.ir</title>
        <style>
            body { font-family: 'Tahoma', sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #333; text-align: center; }
            .status { padding: 10px; background: #e3f2fd; border-radius: 5px; margin: 10px 0; }
            .progress { background: #ddd; border-radius: 10px; height: 20px; margin: 10px 0; }
            .progress-bar { background: #4caf50; height: 100%; border-radius: 10px; transition: width 0.3s; }
            button { background: #2196f3; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 5px; }
            button:hover { background: #0b7dda; }
            button:disabled { background: #ccc; cursor: not-allowed; }
            .results { margin-top: 20px; }
            .result-item { background: #f9f9f9; padding: 10px; margin: 5px 0; border-radius: 5px; word-break: break-all; }
            .success { border-left: 4px solid #4caf50; }
            .error { border-left: 4px solid #f44336; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔗 کوتاه کننده لینک 2AD.ir</h1>
            
            <div class="status" id="status">آماده برای شروع</div>
            
            <div class="progress">
                <div class="progress-bar" id="progressBar" style="width: 0%"></div>
            </div>
            
            <div style="text-align: center;">
                <button onclick="startProcess()" id="startBtn">شروع فرآیند</button>
                <button onclick="stopProcess()" id="stopBtn" disabled>توقف</button>
                <button onclick="downloadResults()" id="downloadBtn">دانلود نتایج</button>
                <button onclick="getStatus()" id="refreshBtn">بروزرسانی</button>
            </div>
            
            <div class="results" id="results"></div>
        </div>

        <script>
            function updateUI() {
                fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('status').textContent = data.status;
                    
                    let progress = data.total_links > 0 ? (data.current_index / data.total_links) * 100 : 0;
                    document.getElementById('progressBar').style.width = progress + '%';
                    
                    document.getElementById('startBtn').disabled = data.is_running;
                    document.getElementById('stopBtn').disabled = !data.is_running;
                    
                    // نمایش نتایج
                    let resultsHtml = '';
                    data.shortened_links.forEach(link => {
                        resultsHtml += `<div class="result-item success">
                            <strong>اصلی:</strong> ${link.original}<br>
                            <strong>کوتاه:</strong> <a href="${link.shortened}" target="_blank">${link.shortened}</a><br>
                            <small>${link.timestamp}</small>
                        </div>`;
                    });
                    
                    data.failed_links.forEach(link => {
                        resultsHtml += `<div class="result-item error">
                            <strong>ناموفق:</strong> ${link.url}<br>
                            <strong>خطا:</strong> ${link.error}<br>
                            <small>${link.timestamp}</small>
                        </div>`;
                    });
                    
                    document.getElementById('results').innerHTML = resultsHtml;
                });
            }
            
            function startProcess() {
                fetch('/api/start', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    updateUI();
                });
            }
            
            function stopProcess() {
                fetch('/api/stop', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    updateUI();
                });
            }
            
            function getStatus() {
                updateUI();
            }
            
            function downloadResults() {
                window.open('/api/download', '_blank');
            }
            
            // بروزرسانی خودکار هر 5 ثانیه
            setInterval(updateUI, 5000);
            updateUI();
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/api/status')
def get_status():
    """وضعیت فعلی"""
    return jsonify({
        'status': shortener.status,
        'is_running': shortener.is_running,
        'current_index': shortener.current_index,
        'total_links': shortener.total_links,
        'shortened_links': shortener.shortened_links[-10:],  # آخرین 10 تا
        'failed_links': shortener.failed_links[-10:]
    })

@app.route('/api/start', methods=['POST'])
def start_process():
    """شروع فرآیند"""
    if shortener.is_running:
        return jsonify({'message': 'فرآیند در حال اجرا است'})
    
    # پاک کردن نتایج قبلی
    shortener.shortened_links.clear()
    shortener.failed_links.clear()
    shortener.current_index = 0
    
    # شروع در thread جدید
    thread = threading.Thread(target=shortener.run_shortening_process)
    thread.start()
    
    return jsonify({'message': 'فرآیند شروع شد'})

@app.route('/api/stop', methods=['POST'])
def stop_process():
    """توقف فرآیند"""
    shortener.is_running = False
    return jsonify({'message': 'درخواست توقف ارسال شد'})

@app.route('/api/download')
def download_results():
    """دانلود نتایج"""
    results = {
        'successful_links': shortener.shortened_links,
        'failed_links': shortener.failed_links,
        'total_processed': len(shortener.shortened_links) + len(shortener.failed_links),
        'success_rate': len(shortener.shortened_links) / (len(shortener.shortened_links) + len(shortener.failed_links)) * 100 if (len(shortener.shortened_links) + len(shortener.failed_links)) > 0 else 0
    }
    
    from flask import Response
    return Response(
        json.dumps(results, ensure_ascii=False, indent=2),
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=shortened_links_results.json'}
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
