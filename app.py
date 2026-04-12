from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'alisher_secret_2026' # Тұрақты кілт
app.permanent_session_lifetime = timedelta(days=7) # 7 күнге сақтау

# Пайдаланушылар
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
        # HTML-дегі name="username" және name="password" арқылы аламыз
        user_input = request.form.get('username')
        pass_input = request.form.get('password')
        
        if user_input in users and users[user_input]['password'] == pass_input:
            session.permanent = True
            session['username'] = user_input
            return redirect(url_for('student_dashboard'))
        else:
            return "Қате! Қайтадан көріңіз."
            
    return render_template('login.html')

@app.route('/student_dashboard')
def student_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Алдыңғы берген student.html кодына қажетті бос тізімдер
    return render_template('student.html', teacher_tasks=[], tasks=[])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
