from flask import Flask, session, redirect, url_for, request, render_template, jsonify
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import os

# 載入環境變數
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key')

# 初始化 OAuth
oauth = OAuth(app)

# Google OAuth 設定
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# GitHub OAuth 設定
github = oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    api_base_url='https://api.github.com/',
    client_kwargs={'scope': 'user:email'},
)


@app.route('/')
def index():
    user = session.get('user')
    return render_template('index.html', user=user)


@app.route('/login/<provider>')
def login(provider):
    """通用登入路由"""
    # 檢查是否為開發中的提供商
    if provider in ['facebook', 'line']:
        return "此登入方式開發測試中，敬請期待！", 501

    if provider not in ['google', 'github']:
        return "不支援的登入提供商", 400

    client = oauth.create_client(provider)
    redirect_uri = url_for('callback', provider=provider, _external=True)
    return client.authorize_redirect(redirect_uri)


@app.route('/callback/<provider>')
def callback(provider):
    """通用回調路由"""
    if provider not in ['google', 'github']:
        return "不支援的登入提供商", 400

    client = oauth.create_client(provider)
    token = client.authorize_access_token()

    # 根據不同提供商獲取用戶資訊
    user_info = get_user_info(provider, client, token)

    # 將用戶資訊存入 session
    session['user'] = user_info
    session['provider'] = provider

    return redirect(url_for('index'))


def get_user_info(provider, client, token):
    """根據不同提供商獲取用戶資訊"""

    if provider == 'google':
        try:
            user_info = client.userinfo(token=token)
            # Google 用戶基本資料
            print("=== Google 用戶基本資料 ===")
            print(f"完整資料: {user_info}")
            return {
                'id': user_info['sub'],
                'name': user_info['name'],
                'email': user_info['email'],
                'picture': user_info.get('picture')
            }
        except Exception as e:
            print(f"Google userinfo 錯誤: {e}")
            # 備用方案：從 token 中獲取
            user_info = token.get('userinfo')
            if user_info:
                return {
                    'id': user_info['sub'],
                    'name': user_info['name'],
                    'email': user_info['email'],
                    'picture': user_info.get('picture')
                }

    elif provider == 'github':
        # GitHub API 調用
        resp = client.get('user')
        user_data = resp.json()

        # GitHub 用戶基本資料
        print("=== GitHub 用戶基本資料 ===")
        print(f"完整資料: {user_data}")

        email_resp = client.get('user/emails')
        emails = email_resp.json()

        print("\n=== GitHub Email 資料 ===")
        print(f"Email 列表: {emails}")

        primary_email = next((email['email']
                             for email in emails if email['primary']), None)
        print(f"主要 Email: {primary_email}")
        print("=" * 40)

        return {
            'id': user_data['id'],
            'name': user_data['name'] or user_data['login'],
            'email': primary_email,
            'picture': user_data['avatar_url']
        }

    return None


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('index'))

    return render_template('profile.html', user=user, provider=session.get('provider'))


if __name__ == '__main__':
    app.run(debug=True, host="localhost", port=8000)
