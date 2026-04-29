from flask import Flask
from flask_session import Session
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from redis import Redis
from routes import register_routes
from operations import get_user_by_id
from dotenv import load_dotenv
from datetime import timedelta
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("KEY")

app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = Redis(host="localhost", port=6379)
app.config["SESSION_PERMANENT"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = False  # HTTPS only turned off because app is always running locally
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

Session(app)

csrf = CSRFProtect(app) # Uses Flask's secret_key

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)