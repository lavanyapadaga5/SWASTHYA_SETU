from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "swasthyasetu_secret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///health.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        if User.query.filter_by(username=uname).first():
            flash("Username already exists.")
        else:
            user = User(username=uname, password=pwd)
            db.session.add(user)
            db.session.commit()
            flash("Registered successfully!")
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        user = User.query.filter_by(username=uname, password=pwd).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials.")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    records = Record.query.filter_by(user_id=user_id).order_by(Record.date.desc()).all()
    return render_template('dashboard.html', records=records)

@app.route('/add', methods=['GET', 'POST'])
def add_record():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['description']
        new_record = Record(user_id=session['user_id'], title=title, description=desc)
        db.session.add(new_record)
        db.session.commit()
        flash("Record added!")
        return redirect(url_for('dashboard'))
    return render_template('add_record.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
