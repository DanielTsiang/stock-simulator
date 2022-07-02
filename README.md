# Stock Simulator

[![Stock Simulator](https://img.shields.io/website-up-down-green-red/https/danieltsiang.github.io.svg)](https://stock-simulator-dt.herokuapp.com/)
[![Test App Status](https://github.com/DanielTsiang/stock-simulator/actions/workflows/test-app.yml/badge.svg)](https://github.com/DanielTsiang/stock-simulator/actions/workflows/test-app.yml)
[![Known Vulnerabilities](https://snyk.io/test/github/DanielTsiang/stock-simulator/badge.svg)](https://snyk.io/test/github/DanielTsiang/stock-simulator)
[![Profile views](https://gpvc.arturio.dev/stock-simulator)](https://gpvc.arturio.dev/stock-simulator)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Buymeacoffee](https://badgen.net/badge/icon/buymeacoffee?icon=buymeacoffee&label)](https://www.buymeacoffee.com/dantsiang8)

## Description
A RESTful web app that simulates managing portfolios of stocks, using real stocks’ prices by querying an API.

## Getting Started
1. Visit the web application [here](https://stock-simulator-dt.herokuapp.com/).
2. Register for an account!

### Running locally
```bash
pip3 install -r requirements.txt
gunicorn application:app --preload
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

## Technologies Used
![Python](https://img.shields.io/badge/python-3670A0?logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?logo=flask&logoColor=white)
![Gunicorn](https://img.shields.io/badge/gunicorn-%298729.svg?logo=gunicorn&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?logo=postgresql&logoColor=white)
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?logo=html5&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-%23563D7C.svg?logo=bootstrap&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?logo=javascript&logoColor=%23F7DF1E)
![jQuery](https://img.shields.io/badge/jquery-%230769AD.svg?logo=jquery&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?logo=githubactions&logoColor=white)
![Dependabot](https://img.shields.io/badge/dependabot-025E8C?logo=dependabot&logoColor=white)
![Heroku](https://img.shields.io/badge/heroku-%23430098.svg?logo=heroku&logoColor=white)

* Python with Flask framework
* Gunicorn
* SQL (SQLite / PostgreSQL)
* HTML5
* CSS with Bootstrap framework
* JavaScript with jQuery framework, and DataTables library
* GitHub Actions workflows for CI to automate running unit tests and apply code formatting
* Dependabot to keep dependencies up to date and mitigate security vulnerabilities
* Heroku for deployment
