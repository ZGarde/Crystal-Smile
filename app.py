import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me-please")

EXCEL_FILE = 'TX-ICO-HOUSTON汇总表.xls'
SHEET_NAME = '汇总表'

USERS = {
    "elite": {"password": "abc123", "clinic": "Houston-Elite Dental Wellness"},
    "mehta": {"password": "xyz456", "clinic": "Houston-Dr. Behramji J. Mehta"},
}

def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return wrapper

def load_data():
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    return df

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = USERS.get(username)
        if user and user['password'] == password:
            session['user'] = username
            session['clinic'] = user['clinic']
            flash('登录成功', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码不正确', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('您已退出登录', 'info')
    return redirect(url_for('login'))

@app.route('/', methods=['GET'])
@login_required
def index():
    keyword = request.args.get('q', '').strip()
    clinic = session.get('clinic')

    df = load_data()
    if '诊所名' in df.columns:
        df = df[df['诊所名'] == clinic]

    if keyword:
        df = df[df.apply(lambda row: row.astype(str).str.contains(keyword, case=False, na=False).any(), axis=1)]

    table_html = df.to_html(classes='table table-striped table-bordered', index=False, border=0)
    return render_template('index.html', table=table_html, keyword=keyword, clinic=clinic, user=session.get('user'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", "10000"))
    app.run(host='0.0.0.0', port=port)