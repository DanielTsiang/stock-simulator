from flask import Blueprint, render_template, request, jsonify

from utils import all_symbols, login_required


symbols_blueprint = Blueprint("symbols", __name__)

# Get valid IEX symbol data
symbols_data, symbols_only_data, symbols_list = all_symbols()


@symbols_blueprint.route("/select_json")
@login_required
def select_json():
    """Returns JSON data for select query for quote and buy modals"""

    symbol_query = request.args.get("q", "")

    # If no symbol query provided
    if not symbol_query:
        return jsonify({"symbols": symbols_only_data})

    # Filter symbol results based on symbol query.
    # Use dict comprehension inside a list comprehension,
    # with if condition to remove unwanted key value pairs from list of dictionaries and filter by value.
    filtered_symbols_only_data = [
        {key: value for key, value in data.items() if key == "Symbol"}
        for data in symbols_data
        if symbol_query.upper() in data["Symbol"]
    ]

    return jsonify({"symbols": filtered_symbols_only_data})


@symbols_blueprint.route("/symbolCheck")
@login_required
def symbolCheck():
    """Check if eligible symbol entered"""

    # Access form data
    if request.args.get("symbol_quote"):
        symbol = request.args.get("symbol_quote").upper()
    elif request.args.get("symbol_buy"):
        symbol = request.args.get("symbol_buy").upper()
    else:
        symbol = request.args.get("symbol_sell").upper()

    # Return True if valid IEX symbol, otherwise return False
    return jsonify(True) if symbol in symbols_list else jsonify(False)


@symbols_blueprint.route("/eligibleSymbols")
@login_required
def eligibleSymbols():
    """Render table of eligible symbols"""

    return render_template("symbols.html")


@symbols_blueprint.route("/symbols_json")
@login_required
def symbols_json():
    """Returns JSON data for eligible symbols"""

    return jsonify({"data": symbols_data})
