使用 Python 搭配 Google Authenticator 進行驗證的正式名稱通常稱為 雙因素認證 (Two-Factor Authentication, 2FA)，
或更具體地稱為 基於時間的一次性密碼 (Time-based One-Time Password, TOTP) 認證。


```
pip install pyotp qrcode[pil]
```



1. 使用 Google Authenticato 掃描生成的 QR 碼
2. 輸入 6位數字一次性密碼
3. 驗證