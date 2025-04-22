# SPEC - 需求說明

## 專案名稱
YouTube/音訊 Gemini 分析器

## 功能說明
本程式可從以下兩種來源取得影音內容並送給 Gemini API 進行語意分析：
- YouTube 影片連結
- 本地端音訊檔案（wav 格式）

並依據選定的 "Prompt 類型"，要求 Gemini 生成以下其中一種回覆：
- `transcript`：影片逐字稿
- `timestamps`：含時間標記的逐字稿
- `summary`：影片重點摘要
- `scene`：場景描述
- `clips`：適合社群分享的短片摘要

分析完成後，將結果儲存成文字檔於 `output/` 目錄中。


## 程式架構

### 1. `get_prompt(prompt_type)`
根據指定的 `prompt_type` 返回對應的提示文字。

### 2. `save_to_file(answer_text, filename)`
將 AI 的回應文字保存到 `output/` 資料夾。

### 3. `send_request(api_key, input_mode, input_path, prompt_type)`
- 選擇 API 模型：固定使用 `gemini-2.5-pro-preview-03-25`
- 支援兩種模式：
  - `youtube` ➔ 傳送 YouTube 影片網址
  - `audio` ➔ 上傳本地音訊檔案（以 Base64 編碼）
- 根據模式組成 payload 並發送 POST 請求至 Gemini API。
- 成功回傳後，解析回答、印出資訊並存檔。

### 4. `encode_audio_base64(filepath)`
將本地音訊檔案轉成 base64 編碼字串（符合 Gemini API 上傳格式）。

### 5. `main 區段`
集中管理可修改的參數，包括：
- `api_key`：你的 Google API 金鑰
- `input_mode`："youtube" 或 "audio"
- `input_path`：影片網址或本地音訊檔案路徑
- `prompt_type`：分析類型選擇

並在最後呼叫 `send_request()` 啟動流程。

## 其它
- `input_mode` 只能是 "youtube" 或 "audio"，輸入錯誤將拋出 `ValueError`。
- 如果是上傳本地音訊，目前預設 mime_type 為 `audio/wav`。
- API 回傳失敗時會顯示 HTTP 錯誤碼與錯誤訊息。
- 產生的輸出檔案會以 `{prompt_type}_{timestamp}.txt` 命名，自動存於 `output/` 資料夾內。


### URL 解釋
- Gemini API
- https://generativelanguage.googleapis.com/v1beta/models/{模型名稱}:{動作}?key={API_KEY}

- 模型清單
- https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}

- 指定模型資訊
- https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash?key={API_KEY}
