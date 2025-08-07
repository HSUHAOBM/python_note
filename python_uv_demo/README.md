# Flask 範例應用程式

Flask 網站範例，使用 **uv** 管理依賴和 Python 版本。

## 關於 uv

**uv** 是一個極快的 Python 套件和專案管理器，使用 Rust 編寫。

**GitHub 專案**: https://github.com/astral-sh/uv

### uv 安裝步驟

#### Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Windows
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 版本升級
```bash
uv self update
```


## 快速開始

### 0. 初始化 uv 專案（如果尚未初始化）

```bash
# 在現有專案中初始化
uv init

# 或創建新專案
uv init my-flask-app
cd my-flask-app
```

### 1. 從 requirements.txt 遷移到 uv

```bash
# 從requirements.txt 添加依賴
uv add -r requirements.txt
```

### 2. 指定 Python 版本

```bash
# 安裝 Python 版本
uv python install 3.11

# 為專案鎖定 Python 版本
uv python pin 3.11

# 查看可用的 Python 版本
uv python list
```

### 3. 安裝依賴

```bash
uv sync
```

### 4. 運行應用程式

```bash
# 使用專案指定的 Python 版本
uv run python app.py

# 或指定特定版本運行
uv run --python 3.11 python app.py
```

## Python 版本管理

### 檢查當前版本

```bash
# 查看專案 Python 版本
uv python pin

# 查看執行時版本
uv run python --version
```

### 切換 Python 版本範例

```bash
# 安裝新版本
uv python install 3.11

# 切換
uv python pin 3.11

# 清理舊環境並重新安裝依賴
uv clean
uv sync

# 驗證切換結果
uv run python --version
```

## 常用 uv 命令

```bash
# 套件管理
uv add flask              # 添加套件
uv remove package-name    # 移除套件
uv sync                   # 同步依賴
uv pip list              # 查看已安裝套件
uv clean                 # 清理環境

# Python 版本
uv python install 3.12   # 安裝 Python 版本
uv python pin 3.11       # 鎖定專案版本
uv python list           # 查看可用版本

# 運行程式
uv run python app.py     # 使用專案 Python 版本
uv shell
```

## 專案結構

```
├── app.py              # Flask 應用程式
├── pyproject.toml      # uv 專案配置 (需版控)
├── uv.lock            # 依賴鎖定檔案 (需版控)
├── .python-version    # Python 版本鎖定 (需版控)
├── .venv/             # 虛擬環境目錄 (不需版控)
├── requirements.txt    # 傳統依賴檔案（遷移後可刪）
└── README.md
```

### uv 相關檔案說明

- **pyproject.toml**: 專案配置和依賴定義
- **uv.lock**: 精確的依賴版本鎖定，確保環境一致性
- **.python-version**: 指定專案使用的 Python 版本
- **.venv/**: 虛擬環境目錄 (加入 .gitignore)

## 路由說明

- `/` - 首頁
- `/hello` - 基本問候
- `/hello/<name>` - 個人化問候
- `/user/<username>` - 用戶資料頁面
- `/api/data` - API 資料端點
- `/form` - 表單範例頁面

## 專案不使用 uv
```bash
uv pip freeze > requirements.txt

rm pyproject.toml
rm uv.lock
rm .python-version
rmdir /s .venv
```