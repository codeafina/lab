from flask import Flask, render_template
from auth.auth import auth_bp, require_login

app = Flask(__name__)

# klucz sesji (dev)
app.secret_key = "dev-secret-key"
app.permanent_session_lifetime = 900  # 15 min

# rejestracja blueprintu
app.register_blueprint(auth_bp)

@app.route("/")
@require_login
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
