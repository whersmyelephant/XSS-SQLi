import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta


app = Flask(__name__, 
            static_folder='static',
            static_url_path='/static',
            template_folder='templates')
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_COOKIE_SECURE'] = False

app.config.update(
    SECRET_KEY='votre_cle_secrete_tres_secure',
    SESSION_COOKIE_NAME='session',
    SESSION_COOKIE_HTTPONLY=False  , #False pour permettre l'accès Js
    SESSION_COOKIE_SECURE=False,  # False pour HTTP en développement
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(minutes=30)
)

db = SQLAlchemy(app)
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')
    full_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    birthdate = db.Column(db.String(20))
    ssn = db.Column(db.String(20))
    address = db.Column(db.String(200))  # Champ ajouté

# Fonction d'initialisation de la base de données
def init_db():
    with app.app_context():
        # Créer les tables si elles n'existent pas
        db.create_all()
        
        # Vérifier et créer l'utilisateur admin
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password=generate_password_hash('adminpass'),
                role='admin',
                full_name='Admin Istrator',
                email='admin@example.com',
                phone='0123456789',
                birthdate='1990-01-01',
                ssn='123-45-6789',
                address='123 Admin Street, Paris'
            )
            db.session.add(admin)
            print("✅ Compte admin créé")
        
        # Vérifier et créer l'utilisateur user1
        if not User.query.filter_by(username='user1').first():
            user1 = User(
                username='user1',
                password=generate_password_hash('userpass'),
                full_name='User One',
                email='user1@example.com',
                phone='9876543210',
                birthdate='1995-05-05',
                ssn='987-65-4321',
                address='456 User Avenue, Lyon'
            )
            db.session.add(user1)
            print("✅ Compte user1 créé")
        
        db.session.commit()
        print("✅ Base de données initialisée")

#supprimer toutes les tables et les recréer
with app.app_context():
    db.drop_all()
    db.create_all()

# Appeler la fonction d'initialisation au démarrage
init_db()

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
            ssn=request.form.get('ssn', ''),
            address=request.form.get('address', '')
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
    # Version sécurisée compatible SQLite
        query = text("SELECT * FROM user WHERE full_name LIKE :search")
        with db.engine.connect() as conn:
            results = conn.execute(query, {"search": f"%{search}%"})
            users = [dict(row) for row in results.mappings()]
    else:
        users = db.session.query(
            User.id, 
            User.username, 
            User.full_name, 
            User.email,
            User.role
        ).all()
    
    return render_template('admin.html', users=users, is_search=bool(search))

if __name__ == '__main__':
    app.run(debug=True, port=5000)