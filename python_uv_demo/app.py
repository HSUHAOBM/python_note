from flask import Flask, render_template, request, jsonify

# 創建 Flask 應用程式實例
app = Flask(__name__)


# 首頁路由
@app.route('/')
def home():
    return '''
    <h1>歡迎使用 Flask 範例應用程式</h1>
    <p>這是一個簡單的 Flask 網站範例</p>
    <ul>
        <li><a href="/hello">問候頁面</a></li>
        <li><a href="/user/張三">用戶頁面範例</a></li>
        <li><a href="/api/data">API 資料範例</a></li>
        <li><a href="/form">表單範例</a></li>
    </ul>
    '''


# 簡單問候頁面
@app.route('/hello')
@app.route('/hello/<name>')
def hello(name=None):
    if name:
        return f'<h1>你好, {name}!</h1><a href="/">回到首頁</a>'
    else:
        return '<h1>你好, 世界!</h1><a href="/">回到首頁</a>'


# 動態路由範例
@app.route('/user/<username>')
def user_profile(username):
    return f'''
    <h1>用戶資料</h1>
    <p>用戶名稱: {username}</p>
    <p>歡迎來到你的個人頁面!</p>
    <a href="/">回到首頁</a>
    '''


# API 路由範例
@app.route('/api/data')
def api_data():
    data = {
        'message': '這是 API 回應',
        'timestamp': '2025-08-07',
        'status': 'success',
        'data': [
            {'id': 1, 'name': '項目1'},
            {'id': 2, 'name': '項目2'},
            {'id': 3, 'name': '項目3'}
        ]
    }
    return jsonify(data)


# 表單頁面
@app.route('/form', methods=['GET', 'POST'])
def form_example():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        return f'''
        <h1>表單提交成功!</h1>
        <p>姓名: {name}</p>
        <p>Email: {email}</p>
        <a href="/form">重新填寫</a> | <a href="/">回到首頁</a>
        '''

    return '''
    <h1>表單範例</h1>
    <form method="POST">
        <p>
            <label>姓名:</label><br>
            <input type="text" name="name" required>
        </p>
        <p>
            <label>Email:</label><br>
            <input type="email" name="email" required>
        </p>
        <p>
            <input type="submit" value="提交">
        </p>
    </form>
    <a href="/">回到首頁</a>
    '''


# 錯誤處理
@app.errorhandler(404)
def page_not_found(e):
    return '''
    <h1>404 - 頁面不存在</h1>
    <p>您要找的頁面不存在。</p>
    <a href="/">回到首頁</a>
    ''', 404


if __name__ == '__main__':
    # 在開發模式下運行
    app.run(debug=True, host='127.0.0.1', port=5000)
