# reCAPTCHA Solver
結合 Selenium 與 Google Gemini API，實現自動辨識與點擊驗證格子。

## 主要功能
- 自動開啟 reCAPTCHA 測試頁面
- 自動勾選「我不是機器人」
- 自動截圖驗證格子
- 透過 Gemini API 辨識圖片內容
- 自動點擊正確格子並提交驗證
- 支援多次題目與自動重試

## 執行環境
- Python 3.8+
- 需安裝 Chrome 瀏覽器
- 需安裝 Google Gemini API 金鑰

## 套件
```bash
pip install selenium webdriver-manager google-generativeai pillow
```

