"""
LINE OAuth 2.0 登入範例 (純 Flask + requests)
"""

import os
import requests
import secrets
from flask import Flask, session, redirect, url_for, request, jsonify
from dotenv import load_dotenv
from urllib.parse import urlencode

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key')

# LINE OAuth 設定
LINE_CLIENT_ID = os.getenv('LINE_CLIENT_ID')
LINE_CLIENT_SECRET = os.getenv('LINE_CLIENT_SECRET')
LINE_REDIRECT_URI = 'http://127.0.0.1:5000/callback/line'

# LINE API 端點
LINE_AUTH_URL = 'https://access.line.me/oauth2/v2.1/authorize'
LINE_TOKEN_URL = 'https://api.line.me/oauth2/v2.1/token'
LINE_VERIFY_URL = 'https://api.line.me/oauth2/v2.1/verify'
LINE_PROFILE_URL = 'https://api.line.me/v2/profile'


@app.route('/')
def index():
    """首頁 - 顯示登入狀態"""
    user = session.get('user')
    if user:
        return f"""
        <h1>歡迎！{user.get('name', 'Unknown')}</h1>
        <p>User ID: {user.get('id')}</p>
        <p>Name: {user.get('name')}</p>
        <p>Email: {user.get('email', '未取得')}</p>
        <p>Picture: <img src="{user.get('picture')}" width="100"></p>
        <a href="/logout">登出</a>
        """
    else:
        return '''
        <h1>LINE OAuth 測試</h1>
        <a href="/line_login">使用 LINE 登入</a>
        '''


@app.route('/line_login')
def line_login():
    """步驟 1: 建立授權 URL 並重導向"""
    # 產生隨機 state 防止 CSRF
    state = secrets.token_urlsafe(32)
    session['oauth_state'] = state

    # 建構授權參數
    auth_params = {
        'response_type': 'code',
        'client_id': LINE_CLIENT_ID,
        'redirect_uri': LINE_REDIRECT_URI,
        'scope': 'profile openid email',
        'state': state
    }

    auth_url = f"{LINE_AUTH_URL}?{urlencode(auth_params)}"
    print(f"=== 步驟 1: 重導向到授權頁面 ===")
    print(f"授權 URL: {auth_url}")

    return redirect(auth_url)


@app.route('/callback/line')
def line_callback():
    """步驟 2: 處理回調並取得用戶資料"""
    # 驗證 state
    state = request.args.get('state')
    if state != session.get('oauth_state'):
        return "State 驗證失敗", 400

    # 取得授權碼
    code = request.args.get('code')
    if not code:
        error = request.args.get('error')
        return f"授權失敗: {error}", 400

    print(f"=== 步驟 2: 收到授權碼 ===")
    print(f"授權碼: {code}")

    # 步驟 3: 換取 token
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': LINE_REDIRECT_URI,
        'client_id': LINE_CLIENT_ID,
        'client_secret': LINE_CLIENT_SECRET
    }

    print(f"=== 步驟 3: 換取 Access Token ===")
    token_response = requests.post(LINE_TOKEN_URL, data=token_data)
    print(f"Status: {token_response.status_code}")
    print(f"Response: {token_response.text}")

    if token_response.status_code != 200:
        return f"取得 token 失敗: {token_response.text}", 400

    token_info = token_response.json()
    access_token = token_info['access_token']

    # 步驟 4A: 使用 ID Token Verify API
    id_token = token_info.get('id_token')
    verify_user_info = None

    if id_token:
        print(f"=== 步驟 4A: ID Token Verify API ===")
        verify_data = {'id_token': id_token, 'client_id': LINE_CLIENT_ID}
        verify_response = requests.post(LINE_VERIFY_URL, data=verify_data)

        print(f"Status: {verify_response.status_code}")
        print(f"Response: {verify_response.text}")

        if verify_response.status_code == 200:
            verify_user_info = verify_response.json()

    # 步驟 4B: 使用 Profile API
    print(f"=== 步驟 4B: Profile API ===")
    profile_headers = {'Authorization': f'Bearer {access_token}'}
    profile_response = requests.get(LINE_PROFILE_URL, headers=profile_headers)

    print(f"Status: {profile_response.status_code}")
    print(f"Response: {profile_response.text}")

    profile_user_info = None
    if profile_response.status_code == 200:
        profile_user_info = profile_response.json()

    # 決定使用哪個資料源
    if verify_user_info:
        final_user_info = {
            'id': verify_user_info.get('sub'),
            'name': verify_user_info.get('name'),
            'picture': verify_user_info.get('picture'),
            'email': verify_user_info.get('email')
        }
    elif profile_user_info:
        final_user_info = {
            'id': profile_user_info.get('userId'),
            'name': profile_user_info.get('displayName'),
            'picture': profile_user_info.get('pictureUrl'),
            'email': None
        }
    else:
        return "無法取得用戶資料", 400

    # 儲存用戶資料到 session
    session['user'] = final_user_info
    session.pop('oauth_state', None)

    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    """登出"""
    session.clear()
    return redirect(url_for('index'))


@app.route('/debug')
def debug():
    """除錯資訊"""
    return jsonify({
        'session': dict(session),
        'config': {
            'LINE_CLIENT_ID': LINE_CLIENT_ID,
            'LINE_REDIRECT_URI': LINE_REDIRECT_URI
        }
    })


if __name__ == '__main__':
    print("=== LINE OAuth 測試伺服器 ===")
    print(f"CLIENT_ID: {LINE_CLIENT_ID}")
    print(f"SECRET: {'已設定' if LINE_CLIENT_SECRET else '未設定'}")
    print(f"回調網址: {LINE_REDIRECT_URI}")
    print("="*40)

    app.run(debug=True, host="127.0.0.1", port=5000)
