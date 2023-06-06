import os
from tempfile import mkdtemp

from cs50 import SQL
from flask import Flask, redirect, request
from flask_session import Session
from werkzeug.exceptions import HTTPException, InternalServerError, default_exceptions

from utils import apology, datetimeformat, usd

# Configure CS50 Library to use PostgreSQL database
uri = os.environ.get("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://")
db = SQL(uri)

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

from routes.buy import buy_blueprint
from routes.cash import cash_blueprint
from routes.history import history_blueprint
from routes.index import index_blueprint
from routes.login import login_blueprint
from routes.password import password_blueprint
from routes.quote import quote_blueprint
from routes.register import register_blueprint
from routes.sell import sell_blueprint
from routes.symbols import symbols_blueprint

# Configure application
app = Flask(__name__)

# Register blueprints
app.register_blueprint(buy_blueprint)
app.register_blueprint(cash_blueprint)
app.register_blueprint(history_blueprint)
app.register_blueprint(index_blueprint)
app.register_blueprint(login_blueprint)
app.register_blueprint(password_blueprint)
app.register_blueprint(quote_blueprint)
app.register_blueprint(register_blueprint)
app.register_blueprint(sell_blueprint)
app.register_blueprint(symbols_blueprint)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.before_request
def before_request():
    # if http is requested then redirect to https
    if request.headers.get("X-Forwarded-Proto") == "http":
        url = request.url.replace("http://", "https://", 1)
        code = 301
        return redirect(url, code=code)


@app.after_request
def after_request(response):
    # Ensure responses aren't cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"

    # Configure HTTP security headers
    response.headers[
        "Strict-Transport-Security"
    ] = "max-age=31536000; includeSubDomains"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    return response


# Custom filters
app.jinja_env.filters["usd"] = usd
app.jinja_env.filters["datetimeformat"] = datetimeformat

# Configure session to use filesystem (instead of signed cookies), and secure cookies
app.config.update(
    SESSION_FILE_DIR=mkdtemp(),
    SESSION_PERMANENT=False,
    SESSION_TYPE="filesystem",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
Session(app)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
