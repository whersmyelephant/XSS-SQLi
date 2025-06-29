from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modèle utilisateur
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    birthdate = db.Column(db.String(20))
    ssn = db.Column(db.String(20))  # Numéro de sécurité sociale

# Créer la base de données
@app.before_first_request
def create_tables():
    db.create_all()
    # Créer un compte admin si inexistant
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password=generate_password_hash('adminpass'),
            role='admin',
            full_name='Admin Istrator',
            email='admin@example.com',
            phone='0123456789',
            birthdate='1990-01-01',
            ssn='123-45-6789'
        )
        db.session.add(admin)
        db.session.commit()
    # Créer un compte utilisateur normal
    if not User.query.filter_by(username='user1').first():
        user1 = User(
            username='user1',
            password=generate_password_hash('userpass'),
            full_name='User One',
            email='user1@example.com',
            phone='9876543210',
            birthdate='1995-05-05',
            ssn='987-65-4321'
        )
        db.session.add(user1)
        db.session.commit()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('profile'))
        else:
            flash('Identifiant ou mot de passe incorrect', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/search')
def search():
    query = request.args.get('q', '')
    # VULN XSS: Injection non échappée
    return render_template('search.html', query=query)

@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Accès refusé', 'danger')
        return redirect(url_for('index'))
    
    search = request.args.get('search', '')
    # VULN SQLi: Injection directe dans la requête
    if search:
        # Version vulnérable à SQLi
        query = f"SELECT * FROM user WHERE full_name LIKE '%{search}%'"
        results = db.engine.execute(query)
    else:
        results = User.query.all()
    
    return render_template('admin.html', users=results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)