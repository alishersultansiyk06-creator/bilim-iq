from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta
import os

app = Flask(__name__)

# Сессия параметрлері
app.secret_key = 'alisher_bilim_iq_2026_key'
app.permanent_session_lifetime = timedelta(days=7)

# ПАЙДАЛАНУШЫЛАР
users = {
    "admin": {"password": "123", "role": "teacher", "username": "Биғалиева Венера (Мұғалім)"},
    "student": {"password": "123", "role": "student", "username": "Сұлтансиық Әлішер"}
}

# МӘЛІМЕТТЕР ҚОРЫНЫҢ ОРНЫНА (Уақытша тізімдер)
# Оқытушы жариялаған тапсырмалар
teacher_tasks_list = [
    {"id": 1, "subject": "Сандық әдістер", "description": "№1 зертханалық жұмыс", "file_url": "#"}
]

# Студенттер жіберген жұмыстар (Мұғалім тексеруі үшін)
submitted_tasks = [
    # Форматы: (Тапсырма мәліметі, Пайдаланушы мәліметі)
    ({"id": 101, "title": "Зертханалық №1", "file_url": "lab1_student.pdf", "grade": "90"}, {"username": "Сұлтансиық Әлішер"})
]

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
            session['username'] = users[user_in]['username']
            session['role'] = users[user_in]['role']
            return redirect(url_for('index'))
        return "Қате! <a href='/login'>Қайтадан</a>"
    return render_template('login.html')

# --- СТУДЕНТ ПОРТАЛЫ ---
@app.route('/student_dashboard')
def student_dashboard():
    if 'username' not in session or session.get('role') != 'student':
        return redirect(url_for('login'))
    
    # Студент өз бағаларын көруі үшін
    my_grades = [task[0] for task in submitted_tasks if task[1]['username'] == session['username']]
    
    return render_template('student.html', 
                           teacher_tasks=teacher_tasks_list, 
                           tasks=my_grades)

# --- МҰҒАЛІМ ПОРТАЛЫ ---
@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'username' not in session or session.get('role') != 'teacher':
        return redirect(url_for('login'))
    
    return render_template('teacher.html', tasks=submitted_tasks)

# ТАПСЫРМА ЖАРИЯЛАУ (Мұғалім үшін)
@app.route('/post_task', methods=['POST'])
def post_task():
    if session.get('role') == 'teacher':
        subject = request.form.get('subject')
        desc = request.form.get('desc')
        # Файлды сақтау логикасы осы жерде болуы керек
        teacher_tasks_list.append({
            "id": len(teacher_tasks_list)+1,
            "subject": subject,
            "description": desc,
            "file_url": "#"
        })
    return redirect(url_for('teacher_dashboard'))

# БАҒА ҚОЮ (Мұғалім үшін)
@app.route('/grade_task/<int:task_id>', methods=['POST'])
def grade_task(task_id):
    grade = request.form.get('grade')
    for task, user in submitted_tasks:
        if task['id'] == task_id:
            task['grade'] = grade
            break
    return redirect(url_for('teacher_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
