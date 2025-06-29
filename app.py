import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    birthdate = db.Column(db.String(20))
    ssn = db.Column(db.String(20))

# Initialisation de la base de données
def init_db():
    with app.app_context():
        db.create_all()
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
            print("✅ Compte admin créé")
        
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
            print("✅ Compte user1 créé")
        
        db.session.commit()
        print("✅ Base de données initialisée")

# Routes
@app.route('/')
def home():
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
            flash('Connexion réussie!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Identifiant ou mot de passe incorrect', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        email = request.form['email']
        
        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Ce nom d\'utilisateur est déjà pris', 'danger')
            return redirect(url_for('register'))
        
        # Créer un nouvel utilisateur
        new_user = User(
            username=username,
            password=generate_password_hash(password),
            full_name=full_name,
            email=email,
            phone=request.form.get('phone', ''),
            birthdate=request.form.get('birthdate', ''),
            ssn=request.form.get('ssn', '')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Compte créé avec succès! Vous pouvez maintenant vous connecter', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/search')
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    query = request.args.get('q', '')
    return render_template('search.html', query=query)

@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Accès non autorisé', 'danger')
        return redirect(url_for('home'))
    
    search = request.args.get('search', '')
    if search:
        # VULN SQLi intentionnelle
        query = f"SELECT * FROM user WHERE full_name LIKE '%{search}%'"
        results = db.engine.execute(query)
    else:
        results = User.query.all()
    
    return render_template('admin.html', users=results)

if __name__ == '__main__':
    # Créer la base de données si elle n'existe pas
    if not os.path.exists('database.db'):
        init_db()
    app.run(debug=True, port=5000)