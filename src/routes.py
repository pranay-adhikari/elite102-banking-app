from flask import render_template, request, redirect, session
import operations

def register_routes(app):

    @app.route("/", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            user = operations.login_user(
                request.form["username"],
                request.form["password"]
            )

            if user:
                session["user_id"] = user[0]
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
    def dashboard():
        if "user_id" not in session:
            return redirect("/", code=302)

        user_id = session["user_id"]

        if request.method == "POST":
            action = request.form["action"]
            amount = float(request.form["amount"])

            if action == "deposit":
                operations.deposit(user_id, amount)
            elif action == "withdraw":
                operations.withdraw(user_id, amount)

        balance = operations.get_balance(user_id)

        return render_template("dashboard.html", balance=balance)

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/")