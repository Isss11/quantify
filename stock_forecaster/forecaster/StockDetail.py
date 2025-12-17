import pandas as pd
import yfinance as yf
import json

# Class that returns basic stock information about the selected stock
class StockDetail:
    def __init__(self, ticker) -> None:
        self.stock = yf.Ticker(ticker)
        
    # Returning relevant information from Yahoo Finance API
    def getGeneralInfo(self):
        try:
            generalInfo = dict()
            generalInfo["tickerSymbol"] = self.stock.info['symbol']
            generalInfo["name"] = self.stock.info["shortName"]
            generalInfo["price"] = self.stock.info["currentPrice"]
            generalInfo["currency"] = self.stock.info["financialCurrency"]
            
            return generalInfo
        except Exception:
            raise ValueError("Unable to obtain ticker details.")
        
if __name__ == "__main__":
    stock = StockDetail("C")
    print(stock.getGeneralInfo())