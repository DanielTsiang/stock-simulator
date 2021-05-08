# Stock Simulator

## Description
A web app that simulates managing portfolios of stocks, using real stocks’ prices by querying an API.

### Demo
<p align="center">
  <img src="https://user-images.githubusercontent.com/74436899/115057720-528e8e00-9edc-11eb-8c97-61a974e3a996.gif" width="600" height="433" alt="demo">
</p>

### Technologies Used
* HTML
* CSS with Bootstrap framework
* JavaScript with jQuery framework, and DataTables library
* Python with Flask framework
* SQL (SQLite / PostgreSQL)

### Specification
* Design and build a RESTful web app using Python with Flask’s MVC framework, connected to a SQL database.
* Users can create an account and login, check stock prices, buy and sell stocks, update cash amount, change password (stored as salted hashes for security), view and clear history of transactions.
* Trading stocks will update the portfolio display and selectable options without page reload via AJAX calls.
* Front-end is styled using CSS with Bootstrap framework, includes popup forms, loading animations and embedded confirmation alerts for enhanced user experience, as well as a mobile-friendly navbar layout.
* Using JavaScript, users can search and sort the stock data displayed in tables.
* User inputs are validated before form submission via jQuery and feedback is shown to user, e.g. error message if password does not meet strong complexity requirements.

### Getting Started
1. Visit the web application [here](https://stock-simulator-dt.herokuapp.com/).
2. Register for an account!

### Contribution Guidelines
If you would like to contribute code, identify bugs, or propose improvements, please fork this repository and submit a pull request with your suggestions. Below are some helpful links to help you get started:
1. [Project's main repository](https://github.com/DanielTsiang/stock-simulator)
2. [Project's issue tracker](https://github.com/DanielTsiang/stock-simulator/issues)

## Usage
```bash
pip3 install -r requirements.txt
flask run
```
