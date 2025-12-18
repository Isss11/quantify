import yfinance as yf
import numpy as np
import pandas as pd

class StockPrices:
    def __init__(self, ticker, sampleStartDate) -> None:
        self.prices = self.retrieveData(ticker, sampleStartDate)
    
    # Retrives data from Yahoo Finance
    # Only need dates and adjusted close data
    def retrieveData(self, ticker, sampleStartDate):
        stockPrices = yf.download(ticker, start=sampleStartDate, multi_level_index=False)
                
        stockPrices = stockPrices.dropna()
        stockPrices = stockPrices.reset_index()
        stockPrices = stockPrices.rename(columns={"Date": "date", "Open": "open", "High": "high", "Low": "low", "Close": "close", "Volume": "volume"})
        stockPrices = stockPrices.drop(columns=['open', 'high', 'low', 'volume'])
        
        return stockPrices
    
    # Obtains an approximation of percentage returns, contingent on the first-differenced series being stationary
    def calculateReturns(self):
        # Constructing a new variable to achieve a stationary process.
        # Getting log difference approximation of percentage changes (a way of first differencing the data)
        self.prices['logClose'] = np.log(self.prices['close'])
        self.prices['logDifClose'] = self.prices['logClose'].diff()
        
        # Convert to percentage changes (and drop top row since it does not have a percentage change)
        self.prices = self.prices.dropna()
        self.prices['logDifClose'] = self.prices['logDifClose'] * 100
        
    # Get final date of recorded returns
    def getFinalRealizedDate(self):
        return self.prices['date'].values[-1]
    
    # Creates a row of normalized data, given a scaler
    def getNormalizedData(self, scaler):
        return scaler.fit_transform(pd.DataFrame(self.prices['close']))