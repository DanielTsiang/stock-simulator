from flask import Blueprint, jsonify, request, session

from application import db
from utils import login_required

cash_blueprint = Blueprint("cash", __name__)


@cash_blueprint.route("/cash", methods=["PUT"])
@login_required
def cash():
    """Update user's cash amount"""

    # Access user's id
    user_id = session["user_id"]

    # Access form data
    cash = float(request.form.get("cash"))
    cash_minor_units = int(cash * 100)

    # Update cash in users table for user
    db.execute("UPDATE users SET cash = ? WHERE id = ?", cash_minor_units, user_id)

    # Return success status
    return jsonify(True)
