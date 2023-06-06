from flask import Blueprint, jsonify, request

from utils import apology, login_required, lookup

quote_blueprint = Blueprint("quote", __name__)


@quote_blueprint.route("/quote")
@login_required
def quote():
    """Get stock quote."""

    if symbol := request.args.get("symbol_quote"):
        return (
            jsonify(QUOTED=quoted, symbol=symbol)
            if (quoted := lookup(symbol))
            else apology("invalid symbol", 400)
        )
    else:
        return apology("must provide quote", 400)
