from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'bilim_iq_2026' # Тұрақты кілт

# Пайдаланушылар базасы (сенің скриншотың бойынша)
users = {
    "student": {"password": "123", "role": "student"},
    "admin": {"password": "123", "role": "teacher"}
}

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('student_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and users[username]['password'] == password:
            session.permanent = True
            session['username'] = username
            return redirect(url_for('student_dashboard'))
        else:
            return "Қате логин немесе пароль!"
    return render_template('login.html')

@app.route('/student_dashboard')
def student_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    # Бос тізімдерді жіберу, әйтпесе Jinja2 қате береді
    return render_template('student.html', teacher_tasks=[], tasks=[])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
