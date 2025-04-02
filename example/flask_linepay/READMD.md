# LINE Pay 串接(Sandbox)


## env
```bash
vi .env
```
```env
LINE_PAY_CHANNEL_ID={你的 LINE PAY 通路 ID}
LINE_PAY_CHANNEL_SECRET={你的 LINE PAY 通路密鑰}
LINE_PAY_CONFIRM_URL={付款成功導向 URL}
LINE_PAY_API_URL=https://sandbox-api-pay.line.me
```
後台管理付款連結 => 管理連結金鑰取 ID & SECRET

## API文件
[LINE Pay API 文件](https://pay.line.me/documents/online_v3_cn.html)

[sandbox](https://developers-pay.line.me/zh/sandbox)

## 流程

```mermaid
graph TD;
    A[前端點付款] --> B["/pay" 建立付款請求]
    B --> C[後端 LINE Pay\n建立交易]
    C --> D[回傳 paymentUrl]
    D --> E[前端跳轉\nLINE Pay 頁面]
    E --> F[付款完成]
    F --> G[前端導向 confirmUrl 顯示付款成功]
    G --> I["/confirm" \n確認付款]
    I --> J["/details" \n查詢付款狀態]
```

