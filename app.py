from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
import os

app = Flask(__name__)

# Сессия тұрақтылығы үшін
app.secret_key = 'bilim_iq_2026_permanent_key'
app.permanent_session_lifetime = timedelta(days=31)

# Пайдаланушылар
users = {
    "admin": {"password": "123", "role": "teacher"},
    "student": {"password": "123", "role": "student"}
}

# Мысал мәліметтер
teacher_tasks_data = [
    {"subject": "IT", "description": "Python-да Flask негіздері", "file_url": "#"}
]
student_submissions = []

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('teacher_dashboard' if session.get('role') == 'teacher' else 'student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_in = request.form.get('username')
        pass_in = request.form.get('password')
        if user_in in users and users[user_in]['password'] == pass_in:
            session.permanent = True
            session['username'] = user_in
            session['role'] = users[user_in]['role']
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/student_dashboard')
def student_dashboard():
    if 'username' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    # HTML-дегі {% for task in tasks %} мен {% for t_task in teacher_tasks %} үшін:
    return render_template('student.html', teacher_tasks=teacher_tasks_data, tasks=student_submissions)

# --- ОСЫ БӨЛІМ СЕНДЕГІ 404 ҚАТЕСІН ЖӨНДЕЙДІ ---
@app.route('/upload_task', methods=['POST'])
def upload_task():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # HTML-дегі name="title" және name="file" арқылы деректерді аламыз
    title = request.form.get('title')
    file = request.files.get('file')
    
    if file and title:
        # Жаңа жіберілген жұмысты тізімге қосамыз (бағасы жоқ, "Тексерілуде" деп шығады)
        student_submissions.append({
            "title": title,
            "grade": None,
            "file_name": file.filename
        })
        print(f"Жаңа жұмыс қабылданды: {title}")
        
    return redirect(url_for('student_dashboard'))

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'username' not in session or session.get('role') != 'teacher':
        return redirect(url_for('login'))
    return render_template('teacher.html', tasks=[])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
