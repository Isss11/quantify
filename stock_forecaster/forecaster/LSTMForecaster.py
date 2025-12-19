import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# FIXME Quick fixes
import yfinance as yf # import yfinance before keras to avoid conflicts
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1' # use CPU

import keras
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from . import StockPrices

TRAIN_PROPORTION = 2/3

# Uses an LSTM model to forecast prices of a given stock
class LSTMForecaster:
    def __init__(self, ticker, sampleStartDate) -> None:
        self.stock = StockPrices.StockPrices(ticker, sampleStartDate)
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        
    # Creates LSTM Model
    def create_model(self, lookBack, epochs, batchSize):
        self.lookBack = lookBack
        self.normalizedPrices = self.stock.get_normalized_data(self.scaler)
        
        # Create training and test data for model evaluation
        # Actual predictions (indicated in the app's UI) will be for data beyond current date
        trainSize = int(len(self.normalizedPrices) * TRAIN_PROPORTION)
        trainingData = self.normalizedPrices[0:trainSize,:]
        testData = self.normalizedPrices[trainSize:len(self.normalizedPrices),:]

        # Create data-set with a given look-back amount
        self.trainX, self.trainY = self.create_dataset(trainingData, self.lookBack)
        self.testX, self.testY = self.create_dataset(testData, self.lookBack)

        # Reshape data to fit with model
        self.trainX = np.reshape(self.trainX, (self.trainX.shape[0], 1, self.trainX.shape[1]))
        self.testX = np.reshape(self.testX, (self.testX.shape[0], 1, self.testX.shape[1]))
        
        self.model = self.get_lstm(self.trainX, self.trainY, epochs, batchSize)
         
    def get_lstm(self, trainX, trainY, epochs, batchSize):
        model = keras.models.Sequential()
        model.add(keras.Input(shape=(1, self.lookBack)))
        model.add(keras.layers.LSTM(4))

        # Adds a neural network layer with one input
        model.add(keras.layers.Dense(1))

        model.compile(loss='mean_squared_error', optimizer='adam')
        model.fit(trainX, trainY, epochs=epochs, batch_size=batchSize)
        
        return model

    def create_dataset(self, dataset, lookBack):
        data_len = len(dataset)
        
        if not self.is_valid_dataset_len(data_len, lookBack):
            raise ValueError("Dataset length is not long enough to compute with look backs.")
        
        dataX, dataY = [], []
        
        for i in range(data_len - lookBack - 1):
            dataX.append(dataset[i:(i + lookBack), 0])
            dataY.append(dataset[i + lookBack, 0])

        return np.array(dataX), np.array(dataY)
    
    def is_valid_dataset_len(self, dataset_len, look_back):
        if dataset_len - look_back - 1 <= 0:
            return False
        
        return True

    # Analyzes quality of model, comparing the results of the training data and test data
    def calc_model_accuracy(self):
        trainPredicted = self.make_forecasts(self.trainX)
        testPredicted = self.make_forecasts(self.testX)
        
        trainActual = self.scaler.inverse_transform([self.trainY])
        testActual = self.scaler.inverse_transform([self.testY])
        
        trainScore = self.compute_error(trainPredicted, trainActual)
        testScore = self.compute_error(testPredicted, testActual)
        
        # Convert Numpy arrays to lists
        newShape = (1, -1)
        trainPredicted = self.get_converted_prices(trainPredicted, newShape)
        testPredicted = self.get_converted_prices(testPredicted, newShape)
        trainActual = self.get_converted_prices(trainActual, newShape)
        testActual = self.get_converted_prices(testActual, newShape)
        
        # Creating a dictionary that provides information on the model's accuracy
        modelAccuracy = dict({"trainPredicted": trainPredicted, "testPredicted": testPredicted, "trainActual": trainActual,
                              "testActual": testActual})
        
        modelDetails = {"rsme" :{"train": trainScore, "test": testScore}}
        
        return modelAccuracy, modelDetails
    
    # Converts numpy array to a list
    def get_converted_prices(self, prices, newShape):
        return np.reshape(prices, newShape).tolist()
        
    def compute_error(self, predicted, actual):
        return np.sqrt(mean_squared_error(actual[0], predicted[:,0]))
    
    # Develops Forecasts
    def make_forecasts(self, X):
        predictions = self.model.predict(X)
        
        # Change predictions back to original units to calculate RMSE in original units
        return self.scaler.inverse_transform(predictions)
        
    # Obtains forecasted values, and combines them into a dictionary with the realized values
    def get_combined_prices(self, forecast_len):        
        realizedPrices = pd.DataFrame(self.stock.prices, columns=['date', 'close'])
                
        # Obtain forecasts to also add in dictionary separately
        forecasted = np.reshape(self.predict_future(forecast_len), (1, -1))[0]
        forecastedDates = self.get_future_dates(forecast_len)
        
        # Creating Data Frame to contain the predicted prices
        forecastedPrices = pd.DataFrame({'date': forecastedDates, 'close': forecasted})
        
        # Remove time from date columns
        realizedPrices['date'] = realizedPrices['date'].dt.date
        forecastedPrices['date'] = forecastedPrices['date'].dt.date
        
        # Organize data into a dictionary to be consumed
        combined_prices = {'realized': {'date': realizedPrices['date'].tolist(), 'prices': realizedPrices['close'].tolist()},
                        'forecasted': {'date': forecastedPrices['date'].tolist(), 'prices': forecastedPrices['close'].tolist()}}
        
        return combined_prices
    
    # Get dates so many days into the future
    def get_future_dates(self, s):
        lastDate = self.stock.getFinalRealizedDate()
        
        dates = []
        
        for i in range(1, s + 1):
            dates.append(lastDate + pd.DateOffset(days=i))
        
        return dates
    
    # Predicts future values beyond the current date
    def predict_future(self, forecast_len):
        # For forecasted values only
        predicted_prices_normalized = []

        # Using look-back amount to append to normalized dataset and using forecasted data to predict future forecasted values
        # Note that this will cause larger errors, but is needed to perform real forecasts
        for i in range(forecast_len):
            # Merging together the predicted and actual prices to use in future forecasts, if there are some predictions made
            if len(predicted_prices_normalized) != 0:
                np_predicted = np.reshape(np.array(predicted_prices_normalized), (-1, 1))    
                combined_prices = np.concatenate((self.normalizedPrices, np_predicted))
            else:
                combined_prices = self.normalizedPrices
            
            # Taking the past amount of values, specified by the lookback amount. This will be used in the model predictions.
            X = np.reshape(combined_prices[-self.lookBack:], (-1, 1, self.lookBack))
            
            # Obtaining predicted price and adding it to the predicted prices array to be used in future forecasts (depending on lookback amount)
            predicted_price = self.model.predict(X)[0][0]
            
            predicted_prices_normalized.append(predicted_price)
            
        predicted_prices = self.scaler.inverse_transform(np.reshape(predicted_prices_normalized, (-1, 1)))
            
        return predicted_prices
        
# Class manual testing code
if __name__ == "__main__":
    forecaster = LSTMForecaster("C", "2010-01-01")
    forecaster.create_model(8)
    
    # Getting forecasted values for 5 days ahead
    print(forecaster.get_combined_prices(5))