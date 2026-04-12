from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
import os

app = Flask(__name__)

# --- СЕССИЯНЫ БЕКІТУ (ЛОГИННЕН ШЫҚПАУ ҮШІН ЕҢ МАҢЫЗДЫ БӨЛІМ) ---
# 1. Секреттік кілтті міндетті түрде тұрақты мәтін қыл. 
# Бұл сервер қайта қосылса да, браузердегі адамды тануға көмектеседі.
app.secret_key = 'bilim_iq_permanent_secret_key_2026' 

# 2. Сессияның өмір сүру уақытын ұзарту (мысалы, 31 күн)
app.permanent_session_lifetime = timedelta(days=31)

# Пайдаланушылар базасы (мұғалім мен студент)
users = {
    "admin": {"password": "123", "role": "teacher", "name": "Биғалиева Венера (Мұғалім)"},
    "student": {"password": "123", "role": "student", "name": "Сұлтансиық Әлішер"}
}

# Тесттік мәліметтер (қате шықпауы үшін)
teacher_tasks = [{"subject": "Информатика", "description": "Python негіздері", "file_url": "#"}]
submitted_tasks = [] 

@app.route('/')
def index():
    # Егер сессия бар болса, рөліне қарай панельге жіберу
    if 'username' in session:
        if session.get('role') == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        return redirect(url_for('student_dashboard'))
    # Сессия жоқ болса ғана логинге жіберу
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # HTML-дегі name="username" және name="password" арқылы аламыз
        user_in = request.form.get('username')
        pass_in = request.form.get('password')
        
        if user_in in users and users[user_in]['password'] == pass_in:
            session.clear() # Ескі қате сессияны тазалау
            session.permanent = True # Сессияны тұрақты (permanent) қылу
            session['username'] = user_in
            session['role'] = users[user_in]['role']
            session['display_name'] = users[user_in]['name']
            return redirect(url_for('index'))
        else:
            return "Қате логин немесе пароль! <a href='/login'>Қайта көру</a>"
            
    return render_template('login.html')

@app.route('/student_dashboard')
def student_dashboard():
    # Тексеріс: Егер сессия жоқ болса немесе рөлі қате болса ғана логинге
    if 'username' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    
    return render_template('student.html', teacher_tasks=teacher_tasks, tasks=[])

@app.route('/teacher_dashboard')
def teacher_dashboard():
    # Тексеріс: Мұғалім екенін растау
    if 'username' not in session or session.get('role') != 'teacher':
        return redirect(url_for('login'))
    
    return render_template('teacher.html', tasks=submitted_tasks)

@app.route('/logout')
def logout():
    session.clear() # Жүйеден шыққанда ғана сессияны жою
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Render-де жұмыс істеуі үшін host пен port
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
