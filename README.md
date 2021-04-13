## Description
A website via which users can create an account to “buy” and “sell” stocks.

### Demo

<img src="https://user-images.githubusercontent.com/74436899/112735596-1f905480-8f45-11eb-9866-be901c8e0812.gif" width="600px" height="433px" alt="demo">

### Specification

* Implement ```register``` in such a way that it allows a user to register for an account via a form.
* Implement ```quote``` in such a way that it allows a user to look up a stock’s current price.
* Implement ```buy``` in such a way that it enables a user to buy stocks.
* Implement ```index``` in such a way that it displays an HTML table summarising, for the user currently logged in, which stocks the user owns, the numbers of shares owned, the current price of each stock, and the total value of each holding (i.e., shares times price). Also display the user’s current cash balance along with a grand total (i.e., stocks’ total value plus cash).
* Implement ```sell``` in such a way that it enables a user to sell shares of a stock (that he or she owns).
* Implement ```history``` in such a way that it displays an HTML table summarising all of a user’s transactions ever, listing row by row each and every buy and every sell.


## Usage
```bash
pip install Flask
flask run
```
