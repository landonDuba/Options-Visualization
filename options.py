import yfinance as yf
import json
from datetime import date
import numpy as np
import mibian
import matplotlib.pyplot as plt
from matplotlib import colors
import matplotlib.patheffects as PathEffects

#Change AAPL to a ticker of your choice
symbol = 'NVDA'
#Change the strike price to your choosing
strike_price = 100


equity = yf.Ticker(symbol)
current_price = equity.info['currentPrice']

#Test share prices +- $20 of the current share price. Change to your choice
share_prices = np.arange(current_price-20, current_price+20, 1)


#All code below this line doesn't need to be edited 

#print(f"current price of {symbol} - ${current_price}")
expiration_date = equity.options[1]
print("Expiration Date: ", expiration_date)

opt = equity.option_chain(expiration_date)

option_data_at_strike = opt.calls.loc[opt.calls['strike'] == strike_price]
implied_volatility = option_data_at_strike['impliedVolatility'].values[0]
print(f"Option Implied Volatility: {implied_volatility}")

current_date_object = date.today()
expiration_date_object = date.fromisoformat(expiration_date)

days_to_expire = (expiration_date_object - current_date_object).days

np.set_printoptions(suppress=True)


#Function to create a 2D Array containing all the predicted prices using the mibian import
def create_value_matrix(prices, number_of_days, strike, implied_volatility):
    output_array = np.zeros((len(prices), number_of_days))
    for i, p in enumerate(prices):
        for d in range(number_of_days):
            bsData = mibian.BS([p, strike, 0, number_of_days - d], volatility=implied_volatility*100)
            price = bsData.callPrice
            output_array[i,d] = round(price, 2)

    return output_array

price_matrix = create_value_matrix(share_prices, days_to_expire, strike_price, implied_volatility)

print(price_matrix)
#print(np.min(price_matrix))
#print(np.max(price_matrix))

#Making a visualization of the matrix with matplotlib
def display_value_matrix(matrix, share_prices, days_to_expire, underlying_price):
    fig, ax = plt.subplots(figsize=(12,12))
    for x in range(days_to_expire):
        for i in range(len(share_prices)-1):
            vmi, vma = np.min(matrix), np.max(matrix)
            vc = (vma + vmi)/2.0
            y = share_prices[i]
            txt = ax.text(x+0.5, y, "{:.2f}".format(matrix[i,x]), ha='center', color = 'k')
    divnorm=colors.TwoSlopeNorm(vmin=vmi, vcenter=vc, vmax=vma)
    ax.imshow(matrix, origin='lower', cmap='RdYlGn', alpha=0.8, extent = [0, days_to_expire, share_prices[0], share_prices[-1]], norm=divnorm)
    #ax.text(0, underlying_price, "Current Price: {:.2f}".format(underlying_price), ha='right', va='top', rotation=45, size=15, bbox=dict(boxstyle='square,pad=0.3', fc="black", ec='b', lw=2))
    ax.grid(which='both', c='black', linewidth=0.9)
    ax.set_aspect(0.2)
    plt.xlabel("Days to Expiration")
    plt.ylabel("Contract Price")
    plt.title("Black-Scholes Derivative Pricing Calculator")
    plt.show()

#Call to display
display_value_matrix(price_matrix, share_prices, days_to_expire, current_price)