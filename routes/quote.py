from flask import Blueprint, escape, jsonify, request

from utils import apology, login_required, lookup

quote_blueprint = Blueprint("quote", __name__)


@quote_blueprint.route("/quote")
@login_required
def quote():
    """Get stock quote."""

    # Access form data
    if symbol := request.args.get("symbol_quote"):
        return (
            jsonify(QUOTED=quoted, symbol=escape(symbol))  # Return quoted information
            if (quoted := lookup(symbol))  # Obtain quote using lookup function
            else apology("invalid symbol", 400)  # Invalid symbol provided
        )
    else:
        # Ensure quote symbol was submitted
        return apology("must provide quote", 400)
