# 判斷是否還有圖片題目
from time import sleep
import google.generativeai as genai
import os
import json
from selenium.webdriver.common.by import By
from google.generativeai import types
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from PIL import Image


# webdriver_manager 會自動根據 google-chrome-stable版本
# 自動在主機內安裝對應的 ChromeDrive 版本，
service = Service(executable_path=ChromeDriverManager().install())


options = webdriver.ChromeOptions()
# 不開啟瀏覽器視窗（無頭模式）
# options.add_argument("--headless")
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


driver.get("https://www.google.com/recaptcha/api2/demo")
# 等待元素載入，最多等 20 秒，條件一達成就馬上繼續，沒達成就報錯
wait = WebDriverWait(driver, 20)

# Google Gemini API 金鑰
API_KEY = ''


# 1. 勾選「我不是機器人」
def click_recaptcha_checkbox(driver, wait):
    """進入 anchor iframe，勾選核取框，回到主頁。"""
    anchor_iframe = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "iframe[src*='anchor']"))
    )
    driver.switch_to.frame(anchor_iframe)
    wait.until(EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))).click()
    print("已勾選『我不是機器人』")
    driver.switch_to.default_content()


# 2. 截圖驗證格子
def capture_bframe_png(driver, wait, outfile="ocr.png"):
    """切入 bframe，截圖其 body，避免空白檔。"""
    bframe = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "iframe[src*='bframe']"))
    )
    driver.switch_to.frame(bframe)
    wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, ".rc-imageselect-tile img")))
    body = driver.find_element(By.TAG_NAME, "body")
    body.screenshot(outfile)
    print(f"✅ 內容已截圖：{outfile}")
    return outfile


# 3. 用 Gemini 辨識圖片
def ask_gemini_for_indexes(png_path):
    """將圖片與提示詞送給 Gemini，取得答案索引。"""
    # 定義提示詞
    PROMPT = '''
    Given a CAPTCHA image displaying a grid, identify all images
    that contain the requested item as per the instruction.
    Return a JSON array of the 0-indexed positions of these images.
    '''
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel("gemini-2.5-flash")
    with open(png_path, "rb") as f:
        img_bytes = f.read()
    response = model.generate_content(
        [
            {"mime_type": "image/png", "data": img_bytes},
            PROMPT
        ],
        generation_config={
            "response_mime_type": "application/json"
        }
    )
    print("✅ 已從 Gemini 獲得索引：", response.text)

    return json.loads(response.text)


# 4. 根據 indexes 點擊格子
def click_tiles_by_indexes(driver, wait, indexes):
    """根據 indexes 點擊 bframe 內對應格子。"""
    tiles = wait.until(EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, '[role="button"].rc-imageselect-tile')))
    for idx in indexes:
        if 0 <= idx < len(tiles):
            try:
                wait.until(EC.element_to_be_clickable(tiles[idx])).click()
                print(f"✅ 已點擊格子 {idx}")
            except Exception as e:
                print(f"⚠️ 點擊格子 {idx} 失敗：{e}")
        else:
            print(f"⚠️  索引 {idx} 超出範圍")
    sleep(1)  # 可視情況調整等待時間


# 5. 點擊『驗證』按鈕
def click_verify_button(driver, wait):
    """在 bframe 內點擊『驗證』。"""
    verify_btn = wait.until(EC.element_to_be_clickable(
        (By.ID, "recaptcha-verify-button")))
    verify_btn.click()
    print("✅ 已點擊『驗證』按鈕")
    driver.switch_to.default_content()


# 判斷是否還有圖片題目
def has_next_captcha(driver):
    """
    回傳 True 表示還有圖片題目，False 表示驗證已通過。
    需切換到 anchor iframe 抓 status。
    """
    try:
        anchor_iframe = driver.find_element(
            By.CSS_SELECTOR, "iframe[src*='anchor']")

        WebDriverWait(driver, 5).until(
            EC.frame_to_be_available_and_switch_to_it(anchor_iframe)
        )
        # 等待狀態元素出現
        status_elem = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located(
                (By.ID, "recaptcha-accessible-status"))
        )

        status = status_elem.get_attribute("innerText")
        driver.switch_to.default_content()

        if "通過驗證" in status:
            return False
    except Exception:
        driver.switch_to.default_content()
        pass

    return True


# ========== 自動化 reCAPTCHA 流程 ==========
# 0. 開啟 reCAPTCHA 頁面
driver.get("https://www.google.com/recaptcha/api2/demo")
click_recaptcha_checkbox(driver, wait)


while True:
    # 1. 截圖驗證格子
    png_path = capture_bframe_png(driver, wait, outfile="ocr.png")
    # 2. 用 Gemini 辨識圖片
    indexes = ask_gemini_for_indexes('ocr.png')
    if not indexes:
        print("⚠️ Gemini 辨識失敗，重試...")
        continue
    # 3. 根據 indexes 點擊格子
    click_tiles_by_indexes(driver, wait, indexes)
    # 4. 點擊『驗證』按鈕
    click_verify_button(driver, wait)
    sleep(2)  # 等待畫面刷新

    # 5. 判斷是否還有圖片題目
    if has_next_captcha(driver):
        print("⚠️ 還有新題目，繼續辨識...")
        continue
    else:
        print("✅ 驗證已通過或進入下一步")
        break

input("請手動確認驗證結果，然後按 Enter 鍵繼續...")
driver.quit()
