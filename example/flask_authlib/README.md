# Flask + Authlib 多平台 OAuth 登入

使用 Authlib 套件實作多個第三方登入（Google、GitHub）。


## 快速開始
### 使用 uv

```bash
pip install uv

uv sync

uv run python app.py
```

## OAuth 2.0 流程說明

### 基本流程：

1. **用戶點擊登入** - 訪問您網站的 `/login/<provider>` 路由
2. **重導向到 OAuth 提供商** - 生成授權 URL 並重導向到對應的 OAuth 提供商
3. **用戶授權** - 在提供商網站登入並同意授權
4. **授權碼回調** - 提供商重導向回您的網站，帶上授權碼
5. **後端換取令牌** - 用授權碼向提供商換取存取令牌
6. **獲取用戶資訊** - 用令牌向提供商 API 請求用戶資訊
7. **登入完成** - 返回登入成功頁面給用戶


## OAuth 應用程式設定

### 1. Google OAuth 設定

#### 申請步驟：
1. **進入 Google Cloud Console**
   ```
   https://console.cloud.google.com/ → 建立新專案 → 專案名稱
   ```

2. **設定 OAuth 同意畫面**
   ```
   左側選單 → API 和服務 → OAuth 同意畫面 → 點擊"開始"
   使用者類型: 外部 → 建立
   ```

3. **建立 OAuth 憑證**
   ```
   左側選單 → API 和服務 → 憑證 → + 建立憑證 → OAuth 2.0 用戶端 ID
   應用程式類型: 網頁應用程式
   已授權的重新導向 URI: http://localhost:8000/callback/google
   → 建立
   ```

4. **獲取認證資訊**
   - 複製 Client ID 和 Client Secret

### 2. GitHub OAuth 設定

#### 申請步驟：
1. **進入設定頁面**
   ```
   GitHub.com → 右上角頭像 → Settings → Developer settings → OAuth Apps → New OAuth App
   ```

2. **填寫應用程式資訊**
   ```
   Application name: Flask OAuth Test
   Homepage URL: http://localhost:8000
   Application description: 測試用的 Flask OAuth 應用程式
   Authorization callback URL: http://localhost:8000/callback/github
   ```

3. **獲取認證資訊**
   - 取得 Client ID、Client Secret


## 環境變數設定

1. 複製 `.env.example` 為 `.env`：
```bash
cp .env.example .env
```

2. 填入各平台的 Client ID 和 Client Secret：
```env
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# GitHub OAuth
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret

# Flask 設定
SECRET_KEY=your_secret_key_here
# 測試模式 (development、production)
FLASK_ENV=development
```



## 程式碼結構

```
Authlib/
├── app.py              # 主應用程式
├── requirements.txt    # Python 依賴
├── .env.example       # 環境變數範例
├── .env              # 實際環境變數（不要提交到 git）
├── templates/
│   ├── index.html    # 首頁
│   └── profile.html  # 用戶資料頁
└── README.md         # 說明文件
```
