01.17 19:18 น.
from flask import Flask, render_template_string, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'council-secret-key'

# ตั้งค่าฐานข้อมูลให้ใช้ path ที่ถูกต้องบน PythonAnywhere
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'council.db')
db = SQLAlchemy(app)

# --- ฐานข้อมูล ---
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# --- HTML Templates ---
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>สภานักเรียนออนไลน์</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;700&display=swap" rel="stylesheet">
    <style>body { font-family: 'Sarabun', sans-serif; background-color: #f8f9fa; }</style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">สภานักเรียน</a>
            <div>
                {% if current_user.is_authenticated %}
                    <a href="/admin" class="btn btn-light btn-sm">ระบบจัดการ</a>
                    <a href="/logout" class="btn btn-outline-light btn-sm">ออกระบบ</a>
                {% else %}
                    <a href="/login" class="btn btn-outline-light btn-sm">ล็อกอินสภา</a>
                {% endif %}
            </div>
        </div>
    </nav>
    <div class="container mt-4">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

INDEX_HTML = """
{% extends "layout" %}
{% block content %}
    <div class="p-4 mb-4 bg-white rounded-3 shadow-sm text-center">
        <h1 class="fw-bold text-primary">ข่าวประชาสัมพันธ์</h1>
    </div>
    <div class="row">
        {% for post in posts %}
        <div class="col-md-6 mb-4">
            <div class="card h-100 shadow-sm border-0">
                <div class="card-body">
                    <h5 class="card-title fw-bold">{{ post.title }}</h5>
                    <p class="card-text text-muted">{{ post.content }}</p>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
{% endblock %}
"""

LOGIN_HTML = """
{% extends "layout" %}
{% block content %}
    <div class="row justify-content-center">
        <div class="col-md-4 card p-4 shadow-sm">
            <h3 class="text-center mb-4">เข้าสู่ระบบสภา</h3>
            <form method="POST">
                <input type="text" name="username" class="form-control mb-2" placeholder="Username" required>
                <input type="password" name="password" class="form-control mb-3" placeholder="Password" required>
                <button type="submit" class="btn btn-primary w-100">ล็อกอิน</button>
            </form>
        </div>
    </div>
{% endblock %}
"""

ADMIN_HTML = """
{% extends "layout" %}
{% block content %}
    <div class="row">
        <div class="col-md-4 card p-4 mb-4">
            <h4>เพิ่มข่าวใหม่</h4>
            <form method="POST">
                <input type="text" name="title" class="form-control mb-2" placeholder="หัวข้อ" required>
                <textarea name="content" class="form-control mb-2" rows="4" placeholder="เนื้อหา" required></textarea>
                <button type="submit" class="btn btn-success w-100">โพสต์ข่าว</button>
            </form>
        </div>
        <div class="col-md-8">
            <h4>รายการข่าว</h4>
            {% for post in posts %}
            <div class="list-group-item d-flex justify-content-between align-items-center mb-2 bg-white p-2 rounded shadow-sm">
                {{ post.title }}
                <a href="/delete/{{ post.id }}" class="btn btn-danger btn-sm">ลบ</a>
            </div>
            {% endfor %}
        </div>
    </div>
{% endblock %}
"""

# --- Routes ---
@app.route('/')
def index():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template_string(HTML_LAYOUT.replace('{% block content %}{% endblock %}', INDEX_HTML), posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '1234':
            login_user(User(1))
            return redirect(url_for('admin'))
    return render_template_string(HTML_LAYOUT.replace('{% block content %}{% endblock %}', LOGIN_HTML))

@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == 'POST':
        new_post = Post(title=request.form['title'], content=request.form['content'])
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('index'))
    posts = Post.query.all()
    return render_template_string(HTML_LAYOUT.replace('{% block content %}{% endblock %}', ADMIN_HTML), posts=posts)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# สร้างตารางข้อมูล
with app.app_context():
    db.create_all()

