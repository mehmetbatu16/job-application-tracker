import os
import re
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'super_secret_session_key_2026'
DATABASE = 'database.db'

def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                company TEXT NOT NULL,
                position TEXT NOT NULL,
                status TEXT NOT NULL,
                date TEXT NOT NULL,
                notes TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()
        conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password):
            error_html = "<div style='background:#e74c3c;color:#fff;padding:15px;border-radius:5px;margin-bottom:20px;font-weight:bold;text-align:center;'>Password must contain at least one uppercase letter and one number!</div>"
            return render_template('register.html', error_message=error_html)
            
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            error_html = "<div style='background:#e74c3c;color:#fff;padding:15px;border-radius:5px;margin-bottom:20px;font-weight:bold;text-align:center;'>Username already exists!</div>"
            return render_template('register.html', error_message=error_html)
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            error_html = "<div style='background:#e74c3c;color:#fff;padding:15px;border-radius:5px;margin-bottom:20px;font-weight:bold;text-align:center;'>Invalid username or password!</div>"
            return render_template('login.html', error_message=error_html)
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    conn = get_db_connection()
    
    if request.method == 'POST':
        company = request.form.get('company', '').strip()
        position = request.form.get('position', '').strip()
        status = request.form.get('status', 'Applied')
        date = request.form.get('date', '2026-05-30')
        notes = request.form.get('notes', '').strip()
        
        if company or position:
            conn.execute(
                'INSERT INTO applications (user_id, company, position, status, date, notes) VALUES (?, ?, ?, ?, ?, ?)',
                (user_id, company, position, status, date, notes)
            )
            conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
        
    apps = conn.execute('SELECT * FROM applications WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    return render_template('dashboard.html', applications=apps, username=session['username'])

@app.route('/delete', methods=['POST'])
def delete_application():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    app_id = request.args.get('id')
    user_id = session['user_id']
    
    if app_id:
        conn = get_db_connection()
        conn.execute('DELETE FROM applications WHERE id = ? AND user_id = ?', (app_id, user_id))
        conn.commit()
        conn.close()
        
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    init_db()
    print("Flask server running successfully on http://127.0.0.1:5003")
    app.run(debug=True, port=5003)