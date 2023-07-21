# Stock Simulator

[![Stock Simulator](https://img.shields.io/website-up-down-green-red/https/danieltsiang.github.io.svg)](https://stock-simulator.onrender.com/)
[![Test App Status](https://github.com/DanielTsiang/stock-simulator/actions/workflows/test-app.yml/badge.svg?&kill_cache=1)](https://github.com/DanielTsiang/stock-simulator/actions/workflows/test-app.yml)
[![Known Vulnerabilities](https://snyk.io/test/github/DanielTsiang/stock-simulator/badge.svg)](https://snyk.io/test/github/DanielTsiang/stock-simulator)
[![Visitors](https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fstock-simulator.onrender.com%2F&label=Hits&countColor=%2337d67a&style=flat)](https://visitorbadge.io/status?path=https%3A%2F%2Fstock-simulator.onrender.com%2F)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Buymeacoffee](https://img.shields.io/badge/Donate-Buy%20Me%20A%20Coffee-orange.svg?style=flat&logo=buymeacoffee)](https://www.buymeacoffee.com/dantsiang8)

## Description
A RESTful web app that simulates managing portfolios of stocks, using real stocks’ prices by querying an API.

## Getting Started
1. Visit the web application [here](https://stock-simulator.onrender.com/).
2. Register for an account!

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
![Render](https://img.shields.io/badge/render-46E3B7.svg?logo=render&logoColor=white)

* Python with Flask framework
* Gunicorn
* SQL (SQLite / PostgreSQL)
* HTML5
* CSS with Bootstrap framework
* JavaScript with jQuery framework, and DataTables library
* GitHub Actions workflows for CI to automate running unit tests
* Dependabot to keep dependencies up to date and mitigate security vulnerabilities
* Render for deployment

## Python
### Running locally with Python
1. Export the following environment variables necessary to run the app, e.g. on MacOS/Linux:
```
export DATABASE_URL=<PostgreSQL database URL>
```
2. In the root folder where `requirements.txt` is contained, run `pip3 install -r requirements.txt` in the terminal to install the requirements for this project.
3. To start the app, in the root folder, run the following command in the terminal:
`gunicorn --log-config logging.conf application:app --preload`
4. Visit `localhost:8000` in your web browser.
5. To shut down the app, in the terminal hit `CTRL+C`.

### Testing locally with Python
In the root folder, run the following commands in the terminal to install the requirements and then run the unit tests:
```
pip3 install -r requirements.txt -r requirements_test.txt
python3 -m unittest discover -s ./tests -p "test*.py"
```

## Docker
### Running locally with Docker
1. Ensure you have Docker installed.
2. To build the Docker image, in the root folder where `application.py` is contained, run the following command in the terminal:
`sh docker/docker-build.sh`
3. Export the following environment variables necessary to run the app, e.g. on MacOS/Linux:
```
export DATABASE_URL=<PostgreSQL database URL>
```
4. To run the Docker container, in the root folder, run the following command in the terminal:
`sh docker/docker-run.sh`
5. Visit `localhost:8000` in your web browser.
6. To shut down the app, in the terminal hit `CTRL+C`.

### Testing locally with Docker
After building the Docker image, run the following command to run the unit tests:
`sh docker/docker-test.sh`
