# pip install -U selenium
# pip install webdriver-manager

# webdriver_manager 會自動根據 google-chrome-stable版本
# 自動在主機內安裝對應的 ChromeDrive 版本，

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

service = Service(executable_path=ChromeDriverManager().install())

# 這些建議都加上，不開頁面、禁用GPU加速等等
options = webdriver.ChromeOptions()
# 不開啟瀏覽器視窗（無頭模式）
options.add_argument("--headless")
# 禁用 GPU 加速，避免 headless 模式下的錯誤
options.add_argument("--disable-gpu")
# 禁用所有瀏覽器擴充功能
options.add_argument("--disable-extensions")
# 移除『Chrome 正受自動測試軟體控制』提示條
options.add_argument("--disable-infobars")
# 啟動時最大化視窗（headless 模式下無效，但可保證解析度）
options.add_argument("--start-maximized")
# 禁用網站通知彈窗
options.add_argument("--disable-notifications")
# 以非沙盒模式執行，解決權限問題（Linux 常用）
options.add_argument('--no-sandbox')
# 避免 /dev/shm 空間不足錯誤（Linux 常用）
options.add_argument('--disable-dev-shm-usage')


driver = webdriver.Chrome(service=service, options=options)

print("Chrome version:", driver.capabilities['browserVersion'])
print("ChromeDriver version:",
      driver.capabilities['chrome']['chromedriverVersion'])


# 開始使用
driver.get('https://www.twse.com.tw/zh/trading/holiday.html')

# input("Press Enter to close the browser...")

# 最後關閉瀏覽器
driver.quit()
