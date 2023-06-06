from flask import Blueprint, flash, jsonify, redirect, render_template, request, session
from werkzeug.security import generate_password_hash

from application import db
from utils import apology

register_blueprint = Blueprint("register", __name__)


@register_blueprint.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via GET
    if request.method == "GET":
        return render_template("register.html")

    # User reached route via POST (as by submitting a form via POST)
    # Access form data
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    # Ensure username was submitted
    if not username:
        return apology("must provide username", 400)

    # Ensure password was submitted
    if not password:
        return apology("must provide password", 400)

    # Ensure password confirmation was submitted
    if not confirmation:
        return apology("must provide password confirmation", 400)

    # Ensure password matches password confirmation
    if password != confirmation:
        return apology("passwords do not match", 400)

    lower_case_username = username.lower()
    if db.execute("SELECT * FROM users WHERE username = ?", lower_case_username):
        # Username already exists
        flash("Username is already taken", "danger")
        return render_template("register.html")

    # Username does not already exist
    # Insert data into database
    user_id = db.execute(
        "INSERT INTO users (username, hash) VALUES (?, ?)",
        lower_case_username,
        generate_password_hash(password),
    )

    # Remember which user has logged in
    session["user_id"] = user_id

    # Redirect user to home page
    return redirect("/")


@register_blueprint.route("/username_check")
def username_check():
    """Check if username already exists"""

    # Access form data
    username = request.args.get("username")
    lower_case_username = username.lower()

    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username = ?", lower_case_username)

    # Return False if username already exists, otherwise return True
    return jsonify(False) if rows else jsonify(True)
