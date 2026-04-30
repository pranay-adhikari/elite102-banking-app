from flask import render_template, request, redirect, session, abort
from flask_login import login_user, login_required, current_user, logout_user
from utils import to_cents, format_cents
import operations

MAX_BALANCE = 2_100_000_000
MAX_DEPOSIT = MAX_BALANCE // 2

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
                session.clear()
                login_user(user, remember=True)
                session.permanent = True
                return redirect("/dashboard")

            return render_template("login.html", error="Invalid credentials")
        return render_template("login.html")

    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            result = operations.create_user(
                request.form["username"],
                request.form["password"]
            )
            
            if result == "ok":
                return redirect("/")
            
            errors = {
                "username_taken": "Username already taken",
                "password_invalid": "Password must be between 8 and 128 characters"
            }

            return render_template("signup.html", error=errors[result])
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
                amount = to_cents(request.form.get("amount")) # Amount in cents to avoid floating point precision errors by storing balances as integers

                if action == "deposit":

                    current_balance = operations.get_balance(user_id)
                    if current_balance + amount > MAX_BALANCE:
                        raise ValueError
                    
                    if not (0 < amount < MAX_DEPOSIT):
                        raise ValueError
                    
                    operations.deposit(user_id, amount)
                    operations.add_transaction(user_id, "deposit", amount)

                elif action == "withdraw":
                    if not (0 < amount < MAX_BALANCE):
                        raise ValueError
                    
                    success = operations.withdraw(user_id, amount)

                    if success:
                        operations.add_transaction(user_id, "withdraw", amount)
                    else:
                        balance = operations.get_balance(user_id)
                        return render_template("dashboard.html", error="Insufficient funds", balance=format_cents(balance))

            except ValueError:
                balance = operations.get_balance(user_id)
                error = "Invalid amount or limit exceeded"
                return render_template("dashboard.html", balance=format_cents(balance), error=error)

        balance = operations.get_balance(user_id)
        return render_template("dashboard.html", balance=format_cents(balance))
    
    @app.route("/transactions")
    @login_required
    def transactions():
        user_id = current_user.id

        rows = operations.get_transactions(user_id)
        return render_template("transactions.html", transactions=rows)

    @app.route("/logout", methods=["POST"])
    @login_required
    def logout():
        session.clear()
        logout_user()
        return redirect("/")