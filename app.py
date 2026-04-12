from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__)
app.secret_key = 'bilim_iq_2026'

# 1. КОНФИГУРАЦИЯ
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 2. МӘЛІМЕТТЕР (Есімдер мен парольдер осында бекітілген)
USERS = {
    'admin': {
        'name': 'Биғалиева Венера', 
        'password': '123', # Мұғалімнің паролі
        'role': 'teacher', 
        'route': 'teacher_dashboard'
    },
    'student': {
        'name': 'Сұлтансиық Әлішер', 
        'password': '321', # Студенттің паролі
        'role': 'student', 
        'route': 'student_dashboard'
    }
}

submissions = []      
teacher_tasks = []    

# 3. МАРШРУТТАР
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('teacher_dashboard' if session['role'] == 'teacher' else 'student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_input = request.form.get('username')
        password_input = request.form.get('password')
        
        session.clear()
        
        # Пайдаланушы бар ма және пароль дұрыс па тексеру
        if username_input in USERS and USERS[username_input]['password'] == password_input:
            user = USERS[username_input]
            session['username'] = user['name']
            session['role'] = user['role']
            return redirect(url_for(user['route']))
        else:
            # Қате болған жағдайда хабарлама жіберу
            flash('Қате логин немесе құпия сөз!', 'danger')
            return redirect(url_for('login'))
            
    return render_template('login.html')

# --- МҰҒАЛІМ БӨЛІМІ ---
@app.route('/post_task', methods=['POST'])
def post_task():
    if session.get('role') != 'teacher': return redirect(url_for('login'))
    
    file = request.files.get('file')
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
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

# --- ПАНЕЛЬДЕР ---
@app.route('/student_dashboard')
def student_dashboard():
    if 'username' not in session: return redirect(url_for('login'))
    user_tasks = [s for s in submissions if s['student_name'] == session.get('username')]
    return render_template('student.html', teacher_tasks=teacher_tasks, tasks=user_tasks)

@app.route('/teacher_dashboard')
def teacher_dashboard():
    if session.get('role') != 'teacher': return redirect(url_for('login'))
    formatted = [(s, {"username": s['student_name']}) for s in submissions]
    return render_template('teacher.html', tasks=formatted)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
