from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta
import os

app = Flask(__name__)

# --- СЕССИЯНЫ ДҰРЫСТАУ ---
# 1. Секреттік кілтті ешқашан os.urandom(24) қылма, өйткені сервер оянған сайын ол өзгереді.
# Төмендегідей тұрақты мән бер:
app.secret_key = 'bilim_iq_super_secret_key_2026' 

# 2. Сессия браузерді жапса да сақталуы үшін:
app.permanent_session_lifetime = timedelta(days=7)

# --- УАҚЫТША БАЗА (Сенің базаң болса, сонымен ауыстыр) ---
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
        
        # Логин мен парольді тексеру
        if username in users and users[username]['password'] == password:
            session.clear() # Жаңадан кірерде ескі сессияны тазалау
            session.permanent = True # Бұл өте маңызды!
            session['username'] = username
            session['role'] = users[username]['role']
            
            if session['role'] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            return redirect(url_for('student_dashboard'))
        else:
            flash("Логин немесе пароль қате!", "danger")
            
    return render_template('login.html')

@app.route('/student_dashboard')
def student_dashboard():
    # Тексеріс: Егер сессия жоқ болса, лақтырып жіберу
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if session.get('role') != 'student':
        return "Бұл бетке кіруге рұқсатыңыз жоқ!"

    # Студентке арналған тапсырмаларды осы жерде базадан аласың
    # Мысалы: tasks = Task.query.all()
    return render_template('student.html', teacher_tasks=[], tasks=[])

@app.route('/teacher_dashboard')
def teacher_dashboard():
    # Тексеріс: Егер сессия жоқ болса, лақтырып жіберу
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if session.get('role') != 'teacher':
        return "Бұл бетке кіруге рұқсатыңыз жоқ!"

    return render_template('teacher.html', tasks=[])

@app.route('/upload_task', methods=['POST'])
def upload_task():
    if 'username' not in session:
        return redirect(url_for('login'))
    # Файл жүктеу логикасы осы жерде...
    flash("Жұмыс сәтті жіберілді!", "success")
    return redirect(url_for('student_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Render немесе басқа хостингке арналған порт баптауы
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
