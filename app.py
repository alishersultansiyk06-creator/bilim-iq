from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta
import os

app = Flask(__name__)

# 1. МАҢЫЗДЫ: Secret key-ді тұрақты қылу. 
# Егер ол os.urandom(24) болса, сервер әр перезагрузкада сессияны өшіреді.
app.secret_key = 'alisher_bilim_iq_2026_key' 

# 2. Сессияның параметрлерін баптау
app.permanent_session_lifetime = timedelta(days=7) # 7 күн бойы логиннен шықпайды

# Мысалы ретінде уақытша база (сенде SQLAlchemy болса, соны қолдан)
users = {
    "admin": {"password": "123", "role": "teacher"},
    "student1": {"password": "123", "role": "student"}
}

@app.route('/')
def index():
    if 'username' in session:
        if session.get('role') == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Пайдаланушыны тексеру
        if username in users and users[username]['password'] == password:
            session.permanent = True  # Сессияны тұрақты қылу
            session['username'] = username
            session['role'] = users[username]['role']
            
            if session['role'] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            return redirect(url_for('student_dashboard'))
        else:
            return "Қате логин немесе пароль!"
            
    return render_template('login.html') # Логин бетінің аты

@app.route('/student_dashboard')
def student_dashboard():
    # ЕГЕР СЕССИЯ ЖОҚ БОЛСА - ЛОГИНГЕ ЖІБЕРУ
    if 'username' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    
    # Бұл жерде базадан тапсырмаларды аласың
    return render_template('student.html')

@app.route('/teacher_dashboard')
def teacher_dashboard():
    # ЕГЕР СЕССИЯ ЖОҚ БОЛСА - ЛОГИНГЕ ЖІБЕРУ
    if 'username' not in session or session.get('role') != 'teacher':
        return redirect(url_for('login'))
        
    return render_template('teacher.html')

@app.route('/logout')
def logout():
    session.clear() # Сессияны толық тазалау
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
