from flask import Blueprint, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash

from application import db
from utils import apology

login_blueprint = Blueprint("login", __name__)


@login_blueprint.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("login.html")

    # User reached route via POST (as by submitting a form via POST)
    # Access form data
    username = request.form.get("username")
    password = request.form.get("password")

    # Ensure username was submitted
    if not username:
        return apology("must provide username", 400)

    # Ensure password was submitted
    elif not password:
        return apology("must provide password", 400)

    # Query database for username
    lower_case_username = username.lower()
    rows = db.execute("SELECT * FROM users WHERE username = ?", lower_case_username)

    # Ensure username exists and password is correct
    if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
        flash("Incorrect username and/or password", "danger")
        return render_template("login.html")

    # Remember which user has logged in
    session["user_id"] = rows[0]["id"]

    # Redirect user to home page
    return redirect("/")


@login_blueprint.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")
