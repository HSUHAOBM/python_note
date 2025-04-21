使用 Flask 來實作 Google Authenticator 的雙因素驗證 (2FA) 功能。
程式會顯示一個 QR code，能夠在 Google Authenticator App 中掃描並啟動 2FA 功能，
並且在登入時要求使用者輸入動態驗證碼。


* /login：登入頁面，使用者輸入帳號和密碼。成功登入後，會檢查該使用者是否已經啟用 2FA，未啟用則導向綁定頁面。
* /bind：綁定 2FA 的頁面，生成 QR code 並要求使用者掃描後輸入驗證碼。
* /verify_2fa：驗證 2FA 的頁面，要求使用者輸入 Google Authenticator 生成的動態驗證碼。
* /protected：受保護的頁面，只有通過 2FA 驗證後才能進入。
* /logout：登出並清除 session。