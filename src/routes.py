from flask import render_template, request, redirect, session
from flask_login import login_user, login_required, current_user, logout_user
from utils import to_cents, format_cents
import operations

MAX_BALANCE = 2_100_000_000
MAX_DEPOSIT = MAX_BALANCE / 2

def register_routes(app):

    @app.route("/", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect("/dashboard")

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
            action = request.form.get("action")

            if action not in ["deposit", "withdraw"]:
                return "Invalid action", 400    
            
            amount = None
            try:
                amount = to_cents(request.form.get("amount")) # Amount in cents to avoid floating point precision errors

                if action == "deposit":

                    current_balance = operations.get_balance(user_id)
                    if current_balance + amount > MAX_BALANCE:
                        raise ValueError
                    
                    if not (0 < amount < MAX_DEPOSIT):
                        raise ValueError
                    
                    operations.deposit(user_id, amount)

                elif action == "withdraw":
                    success = operations.withdraw(user_id, amount)
                    if not success:
                        balance = operations.get_balance(user_id)
                        return render_template("dashboard.html", error="Insufficient funds", balance=format_cents(balance))

            except ValueError:
                balance = operations.get_balance(user_id)
                error = "Invalid amount or limit exceeded"
                return render_template("dashboard.html", balance=format_cents(balance), error=error)
            
            except mysql.connector.errors.DataError:
                balance = operations.get_balance(user_id)
                return render_template("dashboard.html", balance=format_cents(balance), error="System error processing transaction")

        balance = operations.get_balance(user_id)
        return render_template("dashboard.html", balance=format_cents(balance))

    @app.route("/logout", methods=["POST"])
    def logout():
        logout_user()
        return redirect("/")