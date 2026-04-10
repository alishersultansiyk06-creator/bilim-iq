import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'bilim_iq_secret_2026'

# База жолын анықтау
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Пайдаланушы моделі
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(10), nullable=False)

# БАЗАНЫ АВТОМАТТЫ ҚҰРУ ФУНКЦИЯСЫ
def init_db():
    with app.app_context():
        db.create_all()
        # Егер базада ешкім болмаса, тесттік адамдарды қосамыз
        if not User.query.filter_by(username='teacher1').first():
            db.session.add(User(username='teacher1', password='123', role='teacher'))
            db.session.add(User(username='student1', password='123', role='student'))
            db.session.commit()

@app.route('/')
def index():
    # Әр жолы басты бетке кіргенде базаның бар-жоғын тексереді
    init_db()
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('user')
        p = request.form.get('pass')
        user = User.query.filter_by(username=u, password=p).first()
        if user:
            session.update({'user_id': user.id, 'role': user.role})
            return redirect(url_for('teacher_dashboard' if user.role == 'teacher' else 'student_dashboard'))
        return "Қате логин немесе пароль!"
    return render_template('login.html')

@app.route('/teacher')
def teacher_dashboard():
    if session.get('role') != 'teacher': return redirect(url_for('login'))
    return render_template('teacher.html')

@app.route('/student')
def student_dashboard():
    if session.get('role') != 'student': return redirect(url_for('login'))
    return render_template('student.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
