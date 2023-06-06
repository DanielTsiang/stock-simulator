from flask import Blueprint, jsonify, render_template, request, session

from application import db
from utils import datetimeformat, login_required, usd

history_blueprint = Blueprint("history", __name__)


@history_blueprint.route("/history", methods=["GET", "DELETE"])
@login_required
def history():
    """Clear or show history of transactions"""
    # Access user's id
    user_id = session["user_id"]

    # User reached route via GET
    if request.method == "GET":
        return render_template("history.html")

    # User reached route via DELETE (as by submitting a form via DELETE)
    # Clear all of user's transactions
    db.execute("DELETE FROM history WHERE user_id = ?", user_id)

    # Return success status
    return jsonify(True)


@history_blueprint.route("/history_json")
@login_required
def history_json():
    """Returns JSON data for history of transactions"""

    # Access user's id
    user_id = session["user_id"]

    # Obtain history information for logged-in user
    transactions = db.execute(
        "SELECT * FROM history WHERE user_id = ? ORDER BY transacted DESC", user_id
    )

    # Convert to USD price and UK datetime formats
    for transaction in transactions:
        transaction["price"] = usd(transaction["price"])
        transaction["transacted"] = datetimeformat(transaction["transacted"])

    return jsonify({"data": transactions})
