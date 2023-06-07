from flask import Blueprint, jsonify, request, session

from application import db
from utils import apology, login_required, lookup

sell_blueprint = Blueprint("sell", __name__)


@sell_blueprint.route("/sell", methods=["PUT"])
@login_required
def sell():
    """Sell shares of stock"""

    # Access user's id
    user_id = session["user_id"]

    # Access form data
    symbol = request.form.get("symbol_sell")
    shares = int(request.form.get("shares_sell"))

    # Ensure symbol was submitted
    if not symbol:
        return apology("must provide symbol", 400)

    # Ensure shares was submitted
    if not shares:
        return apology("must provide shares", 400)

    # Obtain quote using lookup function
    quoted = lookup(symbol)

    # Check if user has enough shares to sell as requested
    current_shares = db.execute(
        "SELECT shares_count FROM shares WHERE user_id = ? AND symbol = ?",
        user_id,
        symbol,
    )[0]["shares_count"]
    if shares > current_shares:
        return apology("not enough shares owned", 400)

    # User has enough shares to sell as requested
    # Calculate new cash amount user has
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    price = float(quoted[symbol]["currentPrice"])
    price_minor_units = int(price * 100)
    cash_gained = price_minor_units * shares
    new_cash_total = cash + cash_gained

    # Update cash in users table for user
    db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash_total, user_id)

    # Insert sell log into history table
    db.execute(
        "INSERT INTO history (user_id, symbol, shares, price, transacted)"
        "VALUES (?, ?, ?, ?, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))",
        user_id,
        symbol,
        -shares,
        price_minor_units,
    )

    # Keep track of shares in shares table
    new_shares_total = current_shares - shares

    # If 0 shares left of the stock owned
    if new_shares_total == 0:
        db.execute(
            "DELETE FROM shares WHERE user_id = ? AND symbol = ?", user_id, symbol
        )

    # User still owns shares of the stock
    else:
        shares_value_total = new_shares_total * price_minor_units
        db.execute(
            "UPDATE shares SET shares_count = ?, price = ?, total = ? WHERE user_id = ? AND symbol = ?",
            new_shares_total,
            price_minor_units,
            shares_value_total,
            user_id,
            symbol,
        )

    # Return success status
    return jsonify(True)


@sell_blueprint.route("/sell_check")
@login_required
def sell_check():
    """Check if valid shares quantity entered"""

    # Access user's id
    user_id = session["user_id"]

    # Access form data for symbol
    symbol = request.args.get("symbol_sell")

    # User did not supply symbol
    if not symbol:
        return jsonify(True)

    # Access form data for shares quantity
    shares = int(request.args.get("shares_sell"))

    # Select information from shares table for logged-in user
    current_shares = db.execute(
        "SELECT shares_count FROM shares WHERE user_id = ? AND symbol = ?",
        user_id,
        symbol,
    )[0]["shares_count"]

    # Return True if valid shares quantity, otherwise return False
    return jsonify(True) if shares <= current_shares else jsonify(False)


@sell_blueprint.route("/sell_json")
@login_required
def sell_json():
    """Returns JSON data for select query for sell modal"""

    # Access user's id
    user_id = session["user_id"]

    symbol_query = request.args.get("q", "")

    # Select share symbols from shares table for logged-in user
    shares = db.execute("SELECT symbol FROM shares WHERE user_id = ?", user_id)

    # if no symbol query provided
    if not symbol_query:
        return jsonify({"symbols": shares})

    # filter symbol results based on symbol query
    # Use list comprehension with if condition to filter by symbol query
    filtered_shares = [
        data for data in shares if symbol_query.upper() in data["symbol"]
    ]

    return jsonify({"symbols": filtered_shares})
