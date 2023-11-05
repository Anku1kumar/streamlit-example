# Import modules
import requests
import pandas as pd
import streamlit as st 

# Define constants
API_KEY = "C58NDA3V9HQHR5Q1" # Get a free API key from https://www.alphavantage.co/
BASE_URL = "https://www.alphavantage.co/query"
FREE_LIMIT = 100 # The maximum number of trades allowed for free users
SUBSCRIPTION_FEE = 10 # The monthly fee for subscription users 

# Define a class for users
class User:
    def __init__(self, name, email, password, balance=1000, subscribed=False):
        self.name = name
        self.email = email
        self.password = password
        self.balance = balance # The initial balance for paper trading
        self.subscribed = subscribed # Whether the user is subscribed or not
        self.trades = [] # A list of trades made by the user
    
    def get_stock_price(self, symbol):
        # Get the latest stock price from Alpha Vantage API
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": API_KEY
        }
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        if "Global Quote" in data:
            return float(data["Global Quote"]["05. price"])
        else:
            return None
    
    def buy_stock(self, symbol, quantity):
        # Buy a stock and update the balance and trades
        price = self.get_stock_price(symbol)
        if price is not None:
            cost = price * quantity
            if cost <= self.balance:
                self.balance -= cost
                self.trades.append((symbol, quantity, price, "buy"))
                return f"You bought {quantity} shares of {symbol} at ${price:.2f} per share."
            else:
                return f"You do not have enough balance to buy {quantity} shares of {symbol}."
        else:
            return f"Invalid symbol or API error."
    
    def sell_stock(self, symbol, quantity):
        # Sell a stock and update the balance and trades
        price = self.get_stock_price(symbol)
        if price is not None:
            # Check if the user has enough shares to sell
            owned = 0
            for trade in self.trades:
                if trade[0] == symbol and trade[3] == "buy":
                    owned += trade[1]
                elif trade[0] == symbol and trade[3] == "sell":
                    owned -= trade[1]
            if quantity <= owned:
                self.balance += price * quantity
                self.trades.append((symbol, quantity, price, "sell"))
                return f"You sold {quantity} shares of {symbol} at ${price:.2f} per share."
            else:
                return f"You do not have enough shares of {symbol} to sell."
        else:
            return f"Invalid symbol or API error."
    
    def get_portfolio(self):
        # Get the current value and performance of the portfolio
        portfolio = {} # A dictionary of symbol and quantity pairs
        value = 0 # The total value of the portfolio
        profit = 0 # The total profit or loss of the portfolio
        for trade in self.trades:
            symbol, quantity, price, action = trade
            if action == "buy":
                portfolio[symbol] = portfolio.get(symbol, 0) + quantity
                value += price * quantity
                profit -= price * quantity
            elif action == "sell":
                portfolio[symbol] = portfolio.get(symbol, 0) - quantity
                value -= price * quantity
                profit += price * quantity
        # Add the current price of the stocks to the value and profit
        for symbol, quantity in portfolio.items():
            price = self.get_stock_price(symbol)
            if price is not None:
                value += price * quantity
                profit += (price - self.get_stock_price(symbol)) * quantity
        return portfolio, value, profit
    
    def subscribe(self):
        # Subscribe to the service and update the balance and subscription status
        if not self.subscribed:
            if self.balance >= SUBSCRIPTION_FEE:
                self.balance -= SUBSCRIPTION_FEE
                self.subscribed = True
                return f"You have successfully subscribed to the service. You can now make unlimited trades."
            else:
                return f"You do not have enough balance to subscribe to the service. The subscription fee is ${SUBSCRIPTION_FEE}."
        else:
            return f"You are already subscribed to the service." 

# Define a function for the user interface
def main():
    # Create a Streamlit app
    st.title("Paper Trading Site")
    st.sidebar.header("User Login")
    # Get the user input from the sidebar
    name = st.sidebar.text_input("Name")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    # Create a user object with the input
    user = User(name, email, password)
    # Display the user information and balance
    st.subheader(f"Welcome, {user.name}")
    st.write(f"Your email is {user.email}")
    st.write(f"Your balance is ${user.balance:.2f}")
    # Display the subscription status and option
    if user.subscribed:
        st.write(f"You are subscribed to the service. You can make unlimited trades.")
    else:
        st.write(f"You are not subscribed to the service. You can only make {FREE_LIMIT - len(user.trades)} more trades for free.")
        if st.button("Subscribe"):
            message = user.subscribe()
            st.write(message)
    # Display the portfolio and performance
    portfolio, value, profit = user.get_portfolio()
    st.subheader("Your Portfolio")
    st.write(f"Your portfolio value is ${value:.2f}")
    st.write(f"Your portfolio profit/loss is ${profit:.2f}")
    st.write("Your portfolio breakdown:")
    # Display the portfolio as a table
    df = pd.DataFrame.from_dict(portfolio, orient="index", columns=["Quantity"])
    st.table(df)
    # Display the trade options
    st.subheader("Make a Trade")
    # Get the trade input from the user
    symbol = st.text_input("Symbol")
    quantity = st.number_input("Quantity", min_value=1, max_value=100, step=1)
    action = st.selectbox("Action", ["Buy", "Sell"])
    # Check if the user can make a trade
    if user.subscribed or len(user.trades) < FREE_LIMIT:
        # Display the trade confirmation and execute the trade
        if st.button("Confirm Trade"):
            if action == "Buy":
                message = user.buy_stock(symbol, quantity)
            elif action == "Sell":
                message = user.sell_stock(symbol, quantity)
            st.write(message)
    else:
        # Display a message that the user has reached the limit
        st.write(f"You have reached the limit of {FREE_LIMIT} trades for free users. Please subscribe to the service to make more trades.") 

# Run the main function
if __name__ == "__main__":
    main()

