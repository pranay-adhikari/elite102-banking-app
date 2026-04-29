from flask import render_template, request, redirect, session
from flask_login import login_user, login_required, current_user, logout_user
from utils import to_cents, format_cents
import operations

MAX_DEPOSIT = 1_000_000_000_000

def register_routes(app):

    @app.route("/", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            user = operations.authenticate_user(
                request.form["username"],
                request.form["password"]
            )

            if user:
                login_user(user)
                session.permanent = True
                return redirect("/dashboard")

            return render_template("login.html", error="Invalid credentials")
        return render_template("login.html")

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            success = operations.create_user(
                request.form["username"],
                request.form["password"]
            )
            
            if success:
                return redirect("/")
            
            return render_template("signup.html", error="Username aleady taken")
        return render_template("signup.html")

    @app.route("/dashboard", methods=["GET", "POST"])
    @login_required
    def dashboard():
        user_id = current_user.id

        if request.method == "POST":
            action = request.form["action"]

            if action not in ["deposit", "withdraw"]:
                return "Invalid action", 400    
            
            try:
                amount = to_cents(request.form["amount"]) # Balance in cents to avoid floating point precision errors
                if not (0 < amount < MAX_DEPOSIT):
                    raise ValueError
            except ValueError:
                balance = operations.get_balance(user_id)
                return render_template("dashboard.html", balance=format_cents(balance), error="Invalid amount")

            if action == "deposit":
                operations.deposit(user_id, amount)
            elif action == "withdraw":
                success = operations.withdraw(user_id, amount)
                if not success:
                    balance = operations.get_balance(user_id)
                    return render_template("dashboard.html", error="Insufficient funds", balance=format_cents(balance))

        balance = operations.get_balance(user_id)
        return render_template("dashboard.html", balance=format_cents(balance))

    @app.route("/logout", methods=["POST"])
    def logout():
        logout_user()
        return redirect("/")