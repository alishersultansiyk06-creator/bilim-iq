from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'bilim_iq_2026'

# 1. ФАЙЛДАРДЫ САҚТАУҒА АРНАЛҒАН ПАПКА
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Папка жоқ болса, оны автоматты түрде жасау
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Мәліметтер базасының орнына уақытша тізім
submissions = []

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('teacher_dashboard' if session.get('role') == 'teacher' else 'student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        if user == 'admin':
            session['username'] = 'Оқытушы'
            session['role'] = 'teacher'
        else:
            session['username'] = user
            session['role'] = 'student'
        return redirect(url_for('index'))
    return render_template('login.html')

# --- СТУДЕНТТІҢ ФАЙЛ ЖҮКТЕУІ ---
@app.route('/upload_task', methods=['POST'])
def upload_task():
    if 'username' not in session: return redirect(url_for('login'))
    
    title = request.form.get('title')
    file = request.files.get('file')
    
    if title and file:
        # Файлды static/uploads папкасына сақтау
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        # Тізімге ақпаратты қосу
        submissions.append({
            "id": len(submissions) + 1,
            "title": title,
            "student_name": session['username'],
            "file_url": file.filename, # Бұл HTML-дегі файлды ашу үшін керек
            "grade": None
        })
    return redirect(url_for('student_dashboard'))

# --- МҰҒАЛІМНІҢ БАҒА ҚОЮЫ ---
@app.route('/grade_task/<int:task_id>', methods=['POST'])
def grade_task(task_id):
    if session.get('role') != 'teacher': return redirect(url_for('login'))
    
    grade_value = request.form.get('grade')
    
    # Тізімнен керекті тапсырманы тауып, бағасын жаңарту
    for s in submissions:
        if s['id'] == task_id:
            s['grade'] = grade_value
            break
            
    return redirect(url_for('teacher_dashboard'))

@app.route('/student_dashboard')
def student_dashboard():
    my_tasks = [s for s in submissions if s['student_name'] == session['username']]
    return render_template('student.html', teacher_tasks=[], tasks=my_tasks)

@app.route('/teacher_dashboard')
def teacher_dashboard():
    formatted_tasks = [(s, {"username": s['student_name']}) for s in submissions]
    return render_template('teacher.html', tasks=formatted_tasks)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
