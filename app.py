from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import timedelta
import os

app = Flask(__name__)
app.secret_key = 'bilim_iq_2026'
# Сессия браузер жабылғанша сақталуы үшін:
app.permanent_session_lifetime = timedelta(minutes=30)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

USERS = {
    'admin': {
        'name': 'Биғалиева Венера', 
        'password': '123', 
        'role': 'teacher', 
    },
    'student': {
        'name': 'Сұлтансиық Әлішер', 
        'password': '321', 
        'role': 'student', 
    }
}

submissions = []      
teacher_tasks = []    

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
        u_input = request.form.get('username')
        p_input = request.form.get('password')
        
        if u_input in USERS and USERS[u_input]['password'] == p_input:
            session.permanent = True # Сессияны тұрақты ету
            session['username'] = USERS[u_input]['name']
            session['role'] = USERS[u_input]['role']
            
            # Рөліне қарай бағыттау
            if session['role'] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            return redirect(url_for('student_dashboard'))
        else:
            flash('Қате логин немесе құпия сөз!', 'danger')
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/student_dashboard')
def student_dashboard():
    # Тексеруді сәл жеңілдетейік:
    if 'username' not in session:
        return redirect(url_for('login'))
    
    my_tasks = [s for s in submissions if s['student_name'] == session['username']]
    return render_template('student.html', teacher_tasks=teacher_tasks, tasks=my_tasks)

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if 'username' not in session or session.get('role') != 'teacher':
        return redirect(url_for('login'))
        
    formatted = [(s, {"username": s['student_name']}) for s in submissions]
    return render_template('teacher.html', tasks=formatted)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Қалған маршруттарды (post_task, upload_task) осының астына қоса бер...

if __name__ == '__main__':
    app.run(debug=True)
