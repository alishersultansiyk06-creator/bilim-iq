from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'bilim_iq_2026'

# 1. ОРТАҚ ДЕРЕКТЕР ТІЗІМІ (Мұғалім мен Студент осыны көреді)
# Студент жіберген жұмыстар осы тізімге түседі
submissions = []

# Оқытушы жариялаған тапсырмалар
teacher_announcements = []

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('teacher_dashboard' if session.get('role') == 'teacher' else 'student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        if user == 'admin': # Мұғалім
            session['username'] = 'Оқытушы'
            session['role'] = 'teacher'
        else: # Студент
            session['username'] = user
            session['role'] = 'student'
        return redirect(url_for('index'))
    return render_template('login.html')

# --- СТУДЕНТ БЕТІ ---
@app.route('/student_dashboard')
def student_dashboard():
    if session.get('role') != 'student': return redirect(url_for('login'))
    
    # Студент тек өз тапсырмаларын көреді
    my_tasks = [s for s in submissions if s['student_name'] == session['username']]
    return render_template('student.html', teacher_tasks=teacher_announcements, tasks=my_tasks)

# --- ТАПСЫРМАНЫ ҚАБЫЛДАУ (ОСЫ ЖЕРДЕ ҚАТЕ БОЛҒАН) ---
@app.route('/upload_task', methods=['POST'])
def upload_task():
    if 'username' not in session: return redirect(url_for('login'))
    
    title = request.form.get('title')
    file = request.files.get('file')
    
    if title and file:
        # Жаңа жұмысты ортақ submissions тізіміне қосамыз
        new_entry = {
            "id": len(submissions) + 1,
            "title": title,
            "student_name": session['username'],
            "file_url": file.filename,
            "grade": None # Әлі тексерілмеген
        }
        submissions.append(new_entry)
        
    return redirect(url_for('student_dashboard'))

# --- МҰҒАЛІМ БЕТІ ---
@app.route('/teacher_dashboard')
def teacher_dashboard():
    if session.get('role') != 'teacher': return redirect(url_for('login'))
    
    # Мұғалімsubmissions тізіміндегі барлық жұмысты көреді
    # HTML-дегі {% for task, user in tasks %} цикліне сәйкес форматтаймыз
    formatted_tasks = []
    for s in submissions:
        # (Тапсырма мәліметі, Студент мәліметі)
        formatted_tasks.append((s, {"username": s['student_name']}))
        
    return render_template('teacher.html', tasks=formatted_tasks)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
