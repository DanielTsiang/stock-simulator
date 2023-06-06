from flask import Blueprint, jsonify, request

from utils import apology, login_required, lookup

quote_blueprint = Blueprint("quote", __name__)


@quote_blueprint.route("/quote")
@login_required
def quote():
    """Get stock quote."""

    # Access form data
    symbol = request.args.get("symbol_quote")

    # Ensure quote symbol was submitted
    if not symbol:
        return apology("must provide quote", 400)

    # Obtain quote using lookup function
    quoted = lookup(symbol)

    # Invalid symbol provided
    if not quoted:
        return apology("invalid symbol", 400)

    # Return quoted information
    return jsonify(QUOTED=quoted, symbol=symbol)
