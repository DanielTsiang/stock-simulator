from flask import Blueprint, flash, jsonify, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from application import db
from utils import apology, login_required

password_blueprint = Blueprint("password", __name__)


@password_blueprint.route("/password", methods=["GET", "PUT"])
@login_required
def password():
    """Change user's password"""

    # User reached route via GET
    if request.method == "GET":
        return render_template("password.html")

    # User reached route via PUT (as by submitting a form via PUT)
    # Access user's id
    user_id = session["user_id"]

    # Access form data
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    confirmation = request.form.get("confirmation")

    # Ensure old password was submitted
    if not old_password:
        return apology("must provide old password", 400)

    # Ensure new password was submitted
    if not new_password:
        return apology("must provide new password", 400)

    # Ensure password confirmation was submitted
    if not confirmation:
        return apology("must provide password confirmation", 400)

    # Ensure password matches password confirmation
    if new_password != confirmation:
        return apology("passwords do not match", 400)

    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE id = ?", user_id)

    # Ensure old password is correct
    if not check_password_hash(rows[0]["hash"], old_password):
        flash("Incorrect old password", "danger")
        return render_template("password.html")

    # Correct old password
    # Update user's password in database
    db.execute(
        "UPDATE users SET hash = ? WHERE id = ?",
        generate_password_hash(new_password),
        user_id,
    )

    # Return success status
    return jsonify(True)


@password_blueprint.route("/password_check", methods=["POST"])
@login_required
def password_check():
    """Check if user entered correct old password"""

    # Access user's id
    user_id = session["user_id"]

    # Access form data
    old_password = request.form.get("old_password")

    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE id = ?", user_id)

    # Return True if submitted old password is correct, otherwise return False
    return (
        jsonify(True)
        if check_password_hash(rows[0]["hash"], old_password)
        else jsonify(False)
    )
