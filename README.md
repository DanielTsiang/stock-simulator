# Stock Simulator

## Description
A RESTful web app that simulates managing portfolios of stocks, using real stocks’ prices by querying an API.

## Getting Started
1. Visit the web application [here](https://stock-simulator-dt.herokuapp.com/).
2. Register for an account!

### Running locally
```bash
pip3 install -r requirements.txt
flask run
```

### Video Demo
https://user-images.githubusercontent.com/74436899/147715897-edcc5863-2ac8-40cb-9abf-597f02b1aa52.mp4

## Specification
* Design and build a RESTful web app using Python with Flask’s MVC framework, connected to a SQL database. Served by Gunicorn, a production-quality web server.
* Users can create an account and login, check stock prices, buy and sell stocks, update cash amount, change password (stored as salted hashes for security), view and clear history of transactions.
* Trading stocks will update the portfolio display and selectable options without page reload via AJAX calls.
* Front-end is styled using CSS with Bootstrap framework, includes popup forms, loading animations and embedded confirmation alerts for enhanced user experience, as well as a mobile-friendly navbar layout.
* Using JavaScript, users can search and sort the stock data displayed in tables.
* User inputs are validated before form submission via jQuery and feedback is shown to user, e.g. error message if password does not meet strong complexity requirements.

### Technologies Used
* HTML
* CSS with Bootstrap framework
* JavaScript with jQuery framework, and DataTables library
* Python with Flask framework
* SQL (SQLite / PostgreSQL)
