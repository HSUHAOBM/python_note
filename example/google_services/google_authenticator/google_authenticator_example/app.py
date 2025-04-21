import pyotp
import qrcode
from io import BytesIO
from flask import Flask, render_template, request, session, redirect, url_for, flash
from base64 import b64encode
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# 簡單的示例會員帳號密碼
users = {
    'testuser': {
        'password': 'password123',
        # 存儲用戶的 2FA 密鑰
        '2fa_secret': None,
    }
}


# 綁定畫面：生成 QR code，並讓用戶綁定 Google Authenticator
@app.route('/bind', methods=['GET', 'POST'])
def bind():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = users.get(session['username'])
    if user['2fa_secret']:
        flash('已經綁定過 2FA')
        return redirect(url_for('login'))

    if request.method == 'POST':
        token = request.form['token']
        # 使用暫存的 2FA 密鑰進行驗證
        totp = pyotp.TOTP(session['temp_2fa_secret'])

        if totp.verify(token):
            # 驗證碼正確，綁定 2FA 密鑰到用戶
            # 從 session 中移除暫存密鑰
            user['2fa_secret'] = session.pop('temp_2fa_secret')
            flash('2FA 綁定成功，現在可以使用 2FA 登入。')
            return redirect(url_for('login'))
        else:
            flash('驗證碼無效，請重試。')

    # 如果是 GET 請求或驗證失敗，生成新的 QR code
    if 'temp_2fa_secret' not in session:
        # 生成隨機密鑰 (2FA 密鑰)並儲存於 session 中
        session['temp_2fa_secret'] = pyotp.random_base32()

    # 根據這個密鑰 session['temp_2fa_secret'] 創建一個 TOTP 物件
    totp = pyotp.TOTP(session['temp_2fa_secret'])
    uri = totp.provisioning_uri(
        name=session['username'], issuer_name='web_flask_test_2fa')
    qr_img = qrcode.make(uri)

    # 將 QR code 轉換為 base64，便於在網頁上顯示
    buf = BytesIO()
    qr_img.save(buf)
    qr_code_base64 = b64encode(buf.getvalue()).decode('utf-8')

    return render_template('bind.html', qr_code=qr_code_base64)


# 登入畫面：輸入帳號、密碼，並驗證 2FA
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)

        if user and user['password'] == password:
            session['username'] = username
            if user['2fa_secret']:
                return redirect(url_for('verify_2fa'))
            # 如果沒有綁定，去綁定頁面
            return redirect(url_for('bind'))

        flash('登入失敗，帳號或密碼錯誤。')

    return render_template('login.html')


# 2FA 驗證畫面
@app.route('/verify_2fa', methods=['GET', 'POST'])
def verify_2fa():
    if 'username' not in session:
        return redirect(url_for('login'))

    user = users.get(session['username'])

    if request.method == 'POST':
        token = request.form['token']
        totp = pyotp.TOTP(user['2fa_secret'])

        if totp.verify(token):
            flash('登入成功！')
            return redirect(url_for('protected'))
        else:
            flash('驗證失敗，請重試。')

    return render_template('verify_2fa.html')


# 受保護的頁面
@app.route('/protected')
def protected():
    if 'username' not in session:
        return redirect(url_for('login'))
    return f'歡迎，{session["username"]}！這是受保護的頁面。'


# 登出
@app.route('/logout')
def logout():
    session.clear()
    flash('已成功登出')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
