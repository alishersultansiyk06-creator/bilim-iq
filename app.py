from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
import os

app = Flask(__name__)

# СЕССИЯНЫҢ ТҰРАҚТЫЛЫҒЫ ҮШІН МАҢЫЗДЫ
app.secret_key = 'alisher_bilim_iq_2026_key' 
app.permanent_session_lifetime = timedelta(days=7)

# ПАЙДАЛАНУШЫЛАР БАЗАСЫ
users = {
    "admin": {"password": "123", "role": "teacher"},
    "student": {"password": "123", "role": "student"}
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
        # login.html-дегі name="username" және name="password" арқылы аламыз
        user_input = request.form.get('username')
        pass_input = request.form.get('password')
        
        if user_input in users and users[user_input]['password'] == pass_input:
            session.permanent = True
            session['username'] = user_input
            session['role'] = users[user_input]['role'] # Рөлді сақтау
            
            # Рөлге байланысты бағыттау
            if session['role'] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            return "Қате логин немесе пароль! <a href='/login'>Қайтадан көру</a>"
            
    return render_template('login.html')

@app.route('/student_dashboard')
def student_dashboard():
    if 'username' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    
    # student.html-ге қажетті бос тізімдерді жіберу (қате шықпас үшін)
    return render_template('student.html', teacher_tasks=[], tasks=[])

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'username' not in session or session.get('role') != 'teacher':
        return redirect(url_for('login'))
    
    # teacher.html бетінде tasks айнымалысы болса, оны да жіберу керек
    return render_template('teacher.html', tasks=[])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Хостингке арналған порт баптауы
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
