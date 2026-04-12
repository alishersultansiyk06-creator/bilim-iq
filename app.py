import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'bilim_iq_2026_pro'

# База жолы
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- МОДЕЛЬДЕР ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(10), nullable=False) # 'teacher' немесе 'student'
    avatar = db.Column(db.String(200), default='https://cdn-icons-png.flaticon.com/512/149/149071.png')

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(100))
    file_url = db.Column(db.String(200))
    grade = db.Column(db.String(10), nullable=True)
    status = db.Column(db.String(20), default='Жіберілді')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50))
    text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# --- РОУТТАР ---
@app.before_request
def init_db():
    if not os.path.exists(os.path.join(basedir, 'database.db')):
        db.create_all()
        db.session.add(User(username='teacher1', password='123', role='teacher'))
        db.session.add(User(username='student1', password='123', role='student'))
        db.session.commit()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form.get('user'), request.form.get('pass')
        user = User.query.filter_by(username=u, password=p).first()
        if user:
            session.update({'user_id': user.id, 'role': user.role, 'username': user.username})
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    if session['role'] == 'teacher':
        tasks = Assignment.query.all()
        return render_template('teacher.html', tasks=tasks)
    else:
        my_tasks = Assignment.query.filter_by(student_id=session['user_id']).all()
        return render_template('student.html', tasks=my_tasks)

@app.route('/upload', methods=['POST'])
def upload():
    file_url = request.form.get('file_url')
    title = request.form.get('title')
    new_task = Assignment(student_id=session['user_id'], title=title, file_url=file_url)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
