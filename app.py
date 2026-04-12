import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'bilim_iq_final_2026'

# База жолы (Render үшін бапталған)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- МОДЕЛЬДЕР (Кестелер) ---
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
    grade = db.Column(db.String(10), nullable=True) # Мұғалім қоятын баға

# --- БАЗАНЫ ДАЙЫНДАУ ---
@app.before_request
def create_tables():
    # Бұл функция база жоқ болса құрады және тесттік аккаунттарды қосады
    app.before_request_funcs[None].remove(create_tables)
    db.create_all()
    if not User.query.filter_by(username='teacher1').first():
        db.session.add(User(username='teacher1', password='123', role='teacher'))
        db.session.add(User(username='student1', password='123', role='student'))
        db.session.commit()

# --- БЕТТЕР (ROUTES) ---
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
        return "Қате логин немесе пароль!"
    return render_template('login.html')

# Студент панелі
@app.route('/student')
def student_dashboard():
    if session.get('role') != 'student': return redirect(url_for('login'))
    tasks = Assignment.query.filter_by(student_id=session['user_id']).all()
    return render_template('student.html', tasks=tasks)

# Тапсырма жүктеу (Студент)
@app.route('/upload_task', methods=['POST'])
def upload_task():
    if 'user_id' not in session: return redirect(url_for('login'))
    title = request.form.get('title')
    url = request.form.get('url')
    new_task = Assignment(student_id=session['user_id'], title=title, file_url=url)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('student_dashboard'))

# Мұғалім панелі
@app.route('/teacher')
def teacher_dashboard():
    if session.get('role') != 'teacher': return redirect(url_for('login'))
    # Барлық тапсырмаларды студенттің атымен бірге алу
    all_tasks = db.session.query(Assignment, User).join(User).all()
    return render_template('teacher.html', tasks=all_tasks)

# БАҒА ҚОЮ (Мұғалім осы жерде бағаны сақтайды)
@app.route('/grade_task/<int:task_id>', methods=['POST'])
def grade_task(task_id):
    if session.get('role') != 'teacher': return redirect(url_for('login'))
    grade_val = request.form.get('grade')
    task = Assignment.query.get(task_id)
    if task:
        task.grade = grade_val
        db.session.commit() # Базаға біржола сақтау
    return redirect(url_for('teacher_dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
