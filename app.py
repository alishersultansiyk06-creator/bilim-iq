import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'bilim_iq_final_2026'

# --- БАПТАУЛАР ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Файлдарды сақтайтын орынды баптау
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Егер static/uploads папкасы жоқ болса, оны жасау
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
    file_url = db.Column(db.String(200)) # Мұнда файлдың аты сақталады
    grade = db.Column(db.String(10), nullable=True)

class TeacherTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    subject = db.Column(db.String(100))
    description = db.Column(db.Text)
    file_url = db.Column(db.String(200)) # Мұнда файлдың аты сақталады

# Базаны автоматты түрде құру
@app.before_request
def init_db():
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

# Мұғалім панелі
@app.route('/teacher')
def teacher_dashboard():
    if session.get('role') != 'teacher': return redirect(url_for('login'))
    submissions = db.session.query(Assignment, User).join(User).all()
    return render_template('teacher.html', tasks=submissions)

# МҰҒАЛІМ ТАПСЫРМА ЖАРИЯЛАУЫ (ФАЙЛ ЖҮКТЕУМЕН)
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
        file_url=filename # Сұраныс бойынша Drive сілтемесі емес, файл аты
    )
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('teacher_dashboard'))

# Мұғалім баға қоюы
@app.route('/grade_task/<int:task_id>', methods=['POST'])
def grade_task(task_id):
    task = Assignment.query.get(task_id)
    if task:
        task.grade = request.form.get('grade')
        db.session.commit()
    return redirect(url_for('teacher_dashboard'))

# Студент панелі
@app.route('/student')
def student_dashboard():
    if session.get('role') != 'student': return redirect(url_for('login'))
    my_tasks = Assignment.query.filter_by(student_id=session['user_id']).all()
    teacher_tasks = TeacherTask.query.all()
    return render_template('student.html', tasks=my_tasks, teacher_tasks=teacher_tasks)

# СТУДЕНТ ТАПСЫРМА ЖІБЕРУІ (ФАЙЛ ЖҮКТЕУМЕН)
@app.route('/upload_task', methods=['POST'])
def upload_task():
    if 'user_id' not in session: return redirect(url_for('login'))
    
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
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
