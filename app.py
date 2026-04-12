import os
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)

# --- СЕССИЯ ЖӘНЕ ҚАУІПСІЗДІК БАПТАУЛАРЫ ---
# Тұрақты Secret Key (сервер перезагрузка болса да сессия жоғалмайды)
app.secret_key = 'bilim_iq_super_secret_key_2026' 
app.permanent_session_lifetime = timedelta(days=7) # 7 күн бойы логинде тұрады

# --- БАЗА ЖӘНЕ ФАЙЛДАР БАПТАУЫ ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Файлдарды сақтайтын орын
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

db = SQLAlchemy(app)

# --- ДЕРЕКТЕР ҚОРЫНЫҢ ҚҰРЫЛЫМЫ ---

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(10), nullable=False) # 'teacher' немесе 'student'

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(100))
    file_url = db.Column(db.String(200))
    grade = db.Column(db.String(10), nullable=True)

class TeacherTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subject = db.Column(db.String(100))
    description = db.Column(db.Text)
    file_url = db.Column(db.String(200))

# Сессияны әр сұраныс сайын тұрақты қылып бекіту
@app.before_request
def make_session_permanent():
    session.permanent = True
    if not hasattr(app, 'db_created'):
        db.create_all()
        if not User.query.filter_by(username='teacher1').first():
            db.session.add(User(username='teacher1', password='123', role='teacher'))
            db.session.add(User(username='student1', password='123', role='student'))
            db.session.commit()
        app.db_created = True

# --- БАҒЫТТАР (ROUTES) ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('student_dashboard' if session['role'] == 'student' else 'teacher_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form.get('user'), request.form.get('pass')
        user = User.query.filter_by(username=u, password=p).first()
        if user:
            session.update({'user_id': user.id, 'role': user.role, 'username': user.username})
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/teacher')
def teacher_dashboard():
    if session.get('role') != 'teacher': return redirect(url_for('login'))
    # Студенттер жіберген тапсырмалар мен олардың есімдерін қосып алу
    submissions = db.session.query(Assignment, User).join(User, Assignment.student_id == User.id).all()
    return render_template('teacher.html', tasks=submissions)

@app.route('/post_task', methods=['POST'])
def post_task():
    if session.get('role') != 'teacher': return redirect(url_for('login'))
    
    file = request.files.get('file')
    filename = ""
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    new_task = TeacherTask(
        teacher_id=session['user_id'],
        subject=request.form.get('subject'),
        description=request.form.get('desc'),
        file_url=filename
    )
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('teacher_dashboard'))

@app.route('/grade_task/<int:task_id>', methods=['POST'])
def grade_task(task_id):
    if session.get('role') != 'teacher': return redirect(url_for('login'))
    task = Assignment.query.get(task_id)
    if task:
        task.grade = request.form.get('grade')
        db.session.commit()
    return redirect(url_for('teacher_dashboard'))

@app.route('/student')
def student_dashboard():
    if session.get('role') != 'student': return redirect(url_for('login'))
    my_tasks = Assignment.query.filter_by(student_id=session['user_id']).all()
    teacher_tasks = TeacherTask.query.all()
    return render_template('student.html', tasks=my_tasks, teacher_tasks=teacher_tasks)

@app.route('/upload_task', methods=['POST'])
def upload_task():
    if session.get('role') != 'student': return redirect(url_for('login'))
    
    file = request.files.get('file')
    filename = ""
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    new_sub = Assignment(
        student_id=session['user_id'],
        title=request.form.get('title'),
        file_url=filename
    )
    db.session.add(new_sub)
    db.session.commit()
    return redirect(url_for('student_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Render немесе жергілікті жерде іске қосу
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
