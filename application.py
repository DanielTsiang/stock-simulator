import os, time, sqlalchemy.dialects.sqlite, psycopg2

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, datetimeformat, all_symbols

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.before_request
def before_request():
    # if http is requested then redirect to https
    if request.headers.get('X-Forwarded-Proto') == 'http':
        url = request.url.replace('http://', 'https://', 1)
        print("redirected to https?")
        code = 301
        return redirect(url, code=code)


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filters
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["datetimeformat"] = datetimeformat


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use PostgreSQL database
db = SQL(os.getenv("DATA_BASE_URL"))

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

# Get valid IEX symbol data
symbols_data, symbols_only_data, symbols_list = all_symbols()


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    return render_template("index.html")


@app.route("/index_json", methods=["GET"])
@login_required
def index_json():
    """Returns JSON data for index page"""

    # Access user's id
    user_id = session["user_id"]

    # Select information from shares table for logged in user
    SHARES = db.execute("SELECT * FROM shares WHERE user_id = ?", user_id)

    # List comprehension to convert list of dicts into list of symbols
    symbols_owned = [share["symbol"] for share in SHARES]

    # Obtain latest share price(s) from API and update database
    QUOTED = lookup(symbols_owned)

    for share in SHARES:
        price = float(QUOTED[share["symbol"]]["quote"]["latestPrice"])
        new_shares_total = share["shares_count"] * float(QUOTED[share["symbol"]]["quote"]["latestPrice"])
        db.execute("UPDATE shares SET price = ?, total = ? WHERE user_id = ? AND symbol = ?",
                  price, new_shares_total, user_id, share["symbol"])
        share["price"] = price
        share["total"] = new_shares_total

    # Check how much cash the user currently has
    CASH = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]

    return jsonify({"shares_data": SHARES, "cash_data": CASH})


@app.route("/select_json", methods=["GET"])
@login_required
def select_json():
    """Returns JSON data for select query for quote and buy modals"""

    symbol_query = request.args.get("q", "")

    # if no symbol query provided
    if not symbol_query:
        return jsonify({"symbols": symbols_only_data})

    # filter symbol results based on symbol query
    else:
        # Use dict comprehension inside a list comprehension with if condition to remove unwanted key value pairs from list of dictionaries and filter by value
        filtered_symbols_only_data = [{key: value for key, value in data.items() if key == "Symbol"} for data in symbols_data if symbol_query.upper() in data["Symbol"]]

        return jsonify({"symbols": filtered_symbols_only_data})


@app.route("/buy", methods=["POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # Access form data
    symbol = request.form.get("symbol_buy")
    shares = int(request.form.get("shares_buy"))

    # Access user's id
    user_id = session["user_id"]

    # Ensure symbol was submitted
    if not symbol:
        return apology("must provide symbol", 400)

    # Ensure shares was submitted
    if not shares:
        return apology("must provide shares", 400)

    # Obtain quote using lookup function
    QUOTED = lookup(symbol)

    # Ensure valid symbol was submitted
    if QUOTED is None:
        return apology("invalid symbol", 400)

    # Check if user has enough cash to buy shares
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    price = float(QUOTED[symbol]["quote"]["latestPrice"])
    cost = price * shares
    if cash < cost:
        # User does not have enough cash to buy shares
        return apology("can't afford", 400)

    # New amount of cash user has after buying shares
    new_cash_total = cash - cost

    # Update cash in users table for user
    db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash_total, user_id)

    # Insert buy log into history table
    db.execute("INSERT INTO history (user_id, symbol, shares, price, transacted) VALUES (?, ?, ?, ?, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))",
               user_id, symbol, shares, price)

    # Keep track of shares in shares table
    current_shares = db.execute("SELECT shares_count FROM shares WHERE user_id = ? AND symbol = ?", user_id, symbol)

    # If shares have not been bought before
    if not current_shares:
        name = QUOTED[symbol]["quote"]["companyName"]
        db.execute("INSERT INTO shares VALUES (?, ?, ?, ?, ?, ?)",
                   user_id, symbol, name, shares, price, cost)

    # If shares have been bought before
    else:
        new_shares_total = current_shares[0]["shares_count"] + shares
        shares_value_total = new_shares_total * price
        db.execute("UPDATE shares SET shares_count = ?, price = ?, total = ? WHERE user_id = ? AND symbol = ?",
                   new_shares_total, price, shares_value_total, user_id, symbol)

    # Return success status
    return jsonify(True)


@app.route("/buyCheck", methods=["POST"])
@login_required
def buyCheck():
    """Check if user has enough cash to buy requested amount of shares"""

    # Access user's id
    user_id = session["user_id"]

    # Access form data
    symbol = request.form.get("symbol_buy")
    shares = int(request.form.get("shares_buy"))

    # User did not supply symbol
    if not symbol:
        return jsonify(True)

    # Obtain quote using lookup function
    QUOTED = lookup(symbol)

    # Check if user has enough cash to buy shares
    cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
    price = float(QUOTED[symbol]["quote"]["latestPrice"])
    cost = price * shares
    if cash < cost:
        # User does not have enough cash to buy shares
        return jsonify(False)
    else:
        # User has enough cash to buy shares
        return jsonify(True)


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    # Access user's id
    user_id = session["user_id"]

    """Clear or show history of transactions"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Clear all of user's transactions
        test = db.execute("DELETE FROM history WHERE user_id = ?", user_id)

        # Return success status
        return jsonify(True)

    # User reached route via GET
    else:
        return render_template("history.html")


@app.route("/history_json", methods=["GET"])
@login_required
def history_json():
    """Returns JSON data for history of transactions"""

    # Access user's id
    user_id = session["user_id"]

    # Obtain history information for logged in user
    transactions = db.execute("SELECT * FROM history WHERE user_id = ? ORDER BY transacted DESC", user_id)

    # Convert to USD price and UK datetime formats
    for transaction in transactions:
        transaction["price"] = usd(transaction["price"])
        transaction["transacted"] = datetimeformat(transaction["transacted"])

    return jsonify({"data": transactions})


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

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
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Incorrect username and/or password", "danger")
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/quote", methods=["POST"])
@login_required
def quote():
    """Get stock quote."""

    # Access form data
    symbol = request.form.get("symbol_quote")

    # Ensure quote symbol was submitted
    if not symbol:
        return apology("must provide quote", 400)

    # Obtain quote using lookup function
    QUOTED = lookup(symbol)

    # Invalid symbol provided
    if not QUOTED:
        return apology("invalid symbol", 400)

    # Return quoted information
    return jsonify(QUOTED=QUOTED, symbol=symbol)


@app.route("/symbolCheck", methods=["POST"])
@login_required
def symbolCheck():
    """Check if eligible symbol entered"""

    # Access form data
    if request.form.get("symbol_quote"):
        symbol = request.form.get("symbol_quote").upper()
    elif request.form.get("symbol_buy"):
        symbol = request.form.get("symbol_buy").upper()
    else:
        symbol = request.form.get("symbol_sell").upper()

    # Valid IEX symbol
    if symbol in symbols_list:
        return jsonify(True)

    # Invalid IEX symbol
    else:
        return jsonify(False)


@app.route("/sellCheck", methods=["POST"])
@login_required
def sharesCheck():
    """Check if valid shares quantity entered"""

    # Access user's id
    user_id = session["user_id"]

    # Access form data for symbol
    symbol = request.form.get("symbol_sell")

    # User did not supply symbol
    if not symbol:
        return jsonify(True)

    # Access form data for shares quantity
    shares = int(request.form.get("shares_sell"))

    # Select information from shares table for logged in user
    shares_count = db.execute("SELECT shares_count FROM shares WHERE user_id = ? AND symbol = ?", user_id, symbol)[0]["shares_count"]

    # Invalid shares quantity
    if shares > shares_count:
        return jsonify(False)

    # Valid shares quantity
    else:
        return jsonify(True)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Access form data
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted
        elif not confirmation:
            return apology("must provide password confirmation", 400)

        # Ensure password matches password confirmation
        elif password != confirmation:
            return apology("passwords do not match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Username does not already exist
        if not rows:

            # Insert data into database
            user_id = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))

            # Remember which user has logged in
            session["user_id"] = user_id

            # Redirect user to home page
            return redirect("/")

        # Username already exists
        else:
            flash("Username is already taken", "danger")
            return render_template("register.html")

    # User reached route via GET
    else:
        return render_template("register.html")


@app.route("/usernameCheck", methods=["POST"])
def usernameCheck():
    """Check if username already exists"""

    # Access form data
    username = request.form.get("username")

    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE username = ?", username)

    # Username does not already exist
    if not rows:
        return jsonify(True)

    # Username already exists
    else:
        return jsonify(False)


@app.route("/sell", methods=["POST"])
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
    QUOTED = lookup(symbol)

    # Check if user has enough shares to sell as requested
    shares_count = db.execute("SELECT shares_count FROM shares WHERE user_id = ? AND symbol = ?",
                              user_id, symbol)[0]["shares_count"]
    if shares > shares_count:
        return apology("not enough shares owned", 400)

    # User has enough shares to sell as requested
    else:
        # Calculate new cash amount user has
        cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)[0]["cash"]
        price = float(QUOTED[symbol]["quote"]["latestPrice"])
        cash_gained = price * shares
        new_cash_total = cash + cash_gained

        # Update cash in users table for user
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash_total, user_id)

        # Insert sell log into history table
        db.execute("INSERT INTO history (user_id, symbol, shares, price, transacted) VALUES (?, ?, ?, ?, to_char(NOW(), 'YYYY-MM-DD HH24:MI:SS'))",
                   user_id, symbol, -(shares), price)

        # Keep track of shares in shares table
        current_shares = db.execute("SELECT shares_count FROM shares WHERE user_id = ? AND symbol = ?",
                                    user_id, symbol)[0]["shares_count"]
        new_shares_total = current_shares - shares

        # If 0 shares left of the stock owned
        if new_shares_total == 0:
            db.execute("DELETE FROM shares WHERE user_id = ? AND symbol = ?", user_id, symbol)

            # Return success status
            return jsonify(True)

        # User still owns shares of the stock
        else:
            shares_value_total = new_shares_total * price
            db.execute("UPDATE shares SET shares_count = ?, price = ?, total = ? WHERE user_id = ? AND symbol = ?",
                       new_shares_total, price, shares_value_total, user_id, symbol)

            # Return success status
            return jsonify(True)


@app.route("/sell_json", methods=["GET"])
@login_required
def sell_json():
    """Returns JSON data for select query for sell modal"""

    # Access user's id
    user_id = session["user_id"]

    symbol_query = request.args.get("q", "")

    # Select share symbols from shares table for logged in user
    shares = db.execute("SELECT symbol FROM shares WHERE user_id = ?", user_id)

    # if no symbol query provided
    if not symbol_query:
        return jsonify({"symbols": shares})

    # filter symbol results based on symbol query
    else:
        # Use list comprehension with if condition to filter by symbol query
        filtered_shares = [data for data in shares if symbol_query.upper() in data["symbol"]]

        return jsonify({"symbols": filtered_shares})


@app.route("/eligibleSymbols")
@login_required
def eligibleSymbols():
    """Render table of eligible symbols"""

    return render_template("symbols.html")


@app.route("/symbols_json", methods=["GET"])
@login_required
def symbols_json():
    """Returns JSON data for eligible symbols"""

    return jsonify({"data": symbols_data})


@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Change user's password"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

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
        elif not new_password:
            return apology("must provide new password", 400)

        # Ensure password confirmation was submitted
        elif not confirmation:
            return apology("must provide password confirmation", 400)

        # Ensure password matches password confirmation
        elif new_password != confirmation:
            return apology("passwords do not match", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE id = ?", user_id)

        # Ensure old password is correct
        if not check_password_hash(rows[0]["hash"], old_password):
            flash("Incorrect old password", "danger")
            return render_template("password.html")

        # Correct old password
        else:
            # Update user's password in database
            db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(new_password), user_id)

            flash("Password successfully changed", "success")
            return redirect("/")

    # User reached route via GET
    else:
        return render_template("password.html")


@app.route("/passwordCheck", methods=["POST"])
@login_required
def passwordCheck():
    """Check if user entered correct old password"""

    # Access user's id
    user_id = session["user_id"]

    # Access form data
    old_password = request.form.get("old_password")

    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE id = ?", user_id)

    # Ensure old password is correct
    if not check_password_hash(rows[0]["hash"], old_password):
        return jsonify(False)

    # Correct old password
    else:
        return jsonify(True)


@app.route("/cash", methods=["POST"])
@login_required
def cash():
    """Update user's cash amount"""

    # Access user's id
    user_id = session["user_id"]

    # Access form data
    cash = float(request.form.get("cash"))

    # Update cash in users table for user
    db.execute("UPDATE users SET cash = ? WHERE id = ?", cash, user_id)

    # Query database for username
    rows = db.execute("SELECT * FROM users WHERE id = ?", user_id)

    # Return success status
    return jsonify(True)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
