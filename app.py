from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'bilim_iq_2026'

# 1. КОНФИГУРАЦИЯ
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 2. МӘЛІМЕТТЕР (Уақытша база)
USERS = {
    'admin': {'name': '', 'role': 'teacher', 'route': 'teacher_dashboard'},
    'student': {'name': '', 'role': 'student', 'route': 'student_dashboard'}
}

submissions = []      # Студенттер жіберген файлдар
teacher_tasks = []    # Мұғалім жариялаған тапсырмалар

# 3. КӨМЕКШІ ФУНКЦИЯЛАР
def get_current_user():
    return session.get('username')

# 4. МАРШРУТТАР (ROUTES)
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('teacher_dashboard' if session['role'] == 'teacher' else 'student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_input = request.form.get('username')
        session.clear()
        
        # Жүйеде бар қолданушы болса
        if username_input in USERS:
            user = USERS[username_input]
            session['username'] = user['name']
            session['role'] = user['role']
            return redirect(url_for(user['route']))
        
        # Жаңа студент болса
        session['username'] = username_input
        session['role'] = 'student'
        return redirect(url_for('student_dashboard'))
            
    return render_template('login.html')

# --- МҰҒАЛІМ БӨЛІМІ ---
@app.route('/post_task', methods=['POST'])
def post_task():
    if session.get('role') != 'teacher': return redirect(url_for('login'))
    
    file = request.files.get('file')
    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        teacher_tasks.append({
            "subject": request.form.get('subject'),
            "description": request.form.get('desc'),
            "file_url": file.filename
        })
    return redirect(url_for('teacher_dashboard'))

@app.route('/grade_task/<int:task_id>', methods=['POST'])
def grade_task(task_id):
    if session.get('role') == 'teacher':
        for s in submissions:
            if s['id'] == task_id:
                s['grade'] = request.form.get('grade')
    return redirect(url_for('teacher_dashboard'))

# --- СТУДЕНТ БӨЛІМІ ---
@app.route('/upload_task', methods=['POST'])
def upload_task():
    if 'username' not in session: return redirect(url_for('login'))
    
    file = request.files.get('file')
    if file:
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        submissions.append({
            "id": len(submissions) + 1,
            "title": request.form.get('title'),
            "student_name": session['username'],
            "file_url": file.filename,
            "grade": None
        })
    return redirect(url_for('student_dashboard'))

# --- ПАНЕЛЬДЕР (DASHBOARDS) ---
@app.route('/student_dashboard')
def student_dashboard():
    user_tasks = [s for s in submissions if s['student_name'] == session.get('username')]
    return render_template('student.html', teacher_tasks=teacher_tasks, tasks=user_tasks)

@app.route('/teacher_dashboard')
def teacher_dashboard():
    # Мұғалімге деректерді HTML форматына ыңғайлап жіберу
    formatted = [(s, {"username": s['student_name']}) for s in submissions]
    return render_template('teacher.html', tasks=formatted)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
