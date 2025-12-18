import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf # For quick fix, this needs to be imported before tensorflow
import keras
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from . import StockPrices

# Uses an LSTM model to forecast prices of a given stock
class LSTMForecaster:
    def __init__(self, ticker, sampleStartDate) -> None:
        self.stock = StockPrices.StockPrices(ticker, sampleStartDate)
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        
    # Creates LSTM Model
    def createModel(self, lookBack, epochs, batchSize):
        self.lookBack = lookBack
        
        self.normalizedPrices = self.stock.getNormalizedData(self.scaler)
        
        # Create training and test data for model evaluation
        # Actual predictions (indicated in the app's UI) will be for data beyond current date
        trainSize = int(len(self.normalizedPrices) * 0.7)
        
        trainingData = self.normalizedPrices[0:trainSize,:]
        testData = self.normalizedPrices[trainSize:len(self.normalizedPrices),:]
        
        # Create data-set with a given look-back amount
        self.trainX, self.trainY = self.createDataset(trainingData, self.lookBack)
        self.testX, self.testY = self.createDataset(testData, self.lookBack)
        
        # Reshape data to fit with model
        self.trainX = np.reshape(self.trainX, (self.trainX.shape[0], 1, self.trainX.shape[1]))
        self.testX = np.reshape(self.testX, (self.testX.shape[0], 1, self.testX.shape[1]))
        
        self.model = self.getLSTM(self.trainX, self.trainY, epochs, batchSize)
        
    def getLSTM(self, trainX, trainY, epochs, batchSize):
        model = keras.models.Sequential()
        model.add(keras.Input(shape=(1, self.lookBack)))
        model.add(keras.layers.LSTM(4, return_sequences=True))

        # Adds a neural network layer with one input
        model.add(keras.layers.Dense(1))

        model.compile(loss='mean_squared_error', optimizer='adam')
        model.fit(trainX, trainY, epochs=epochs, batch_size=batchSize, verbose=2)
        
        return model

    def createDataset(self, dataset, lookBack):
        dataX, dataY = [], []
    
        for i in range(len(dataset)-lookBack-1):
            a = dataset[i:(i + lookBack), 0]
            dataX.append(a)
            dataY.append(dataset[i + lookBack, 0])

        return np.array(dataX), np.array(dataY)
    
    # Analyzes quality of model, comparing the results of the training data and test data
    def getModelAccuracy(self):
        trainPredicted = self.makeForecasts(self.trainX)
        testPredicted = self.makeForecasts(self.testX)
        
        trainActual = self.scaler.inverse_transform([self.trainY])
        testActual = self.scaler.inverse_transform([self.testY])
        
        trainScore = self.computeError(trainPredicted, trainActual)
        testScore = self.computeError(testPredicted, testActual)
        
        # Convert Numpy arrays to lists
        newShape = (1, -1)
        trainPredicted = self.getConvertedPrices(trainPredicted, newShape)
        testPredicted = self.getConvertedPrices(testPredicted, newShape)
        trainActual = self.getConvertedPrices(trainActual, newShape)
        testActual = self.getConvertedPrices(testActual, newShape)
        
        # Creating a dictionary that provides information on the model's accuracy
        modelAccuracy = dict({"trainPredicted": trainPredicted, "testPredicted": testPredicted, "trainActual": trainActual,
                              "testActual": testActual})
        
        modelDetails = {"rsme" :{"train": trainScore, "test": testScore}}
        
        return modelAccuracy, modelDetails
    
    # Converts numpy array to a list
    def getConvertedPrices(self, prices, newShape):
        return np.reshape(prices, newShape).tolist()
        
    def computeError(self, predicted, actual):
        return np.sqrt(mean_squared_error(actual[0], predicted[:,0]))
    
    # Develops Forecasts
    def makeForecasts(self, X):
        predictions = self.model.predict(X)
        
        # Change predictions back to original units to calculate RMSE in original units
        return self.scaler.inverse_transform(predictions)
        
    # Obtains forecasted values, and combines them into a dictionary with the realized values
    def getCombinedPrices(self, s):
        realizedPrices = pd.DataFrame(self.stock.prices, columns=['date', 'adjClose'])
                
        # Obtain forecasts to also add in dictionary separately
        forecasted = np.reshape(self.predictIntoFuture(s), (1, -1))[0]
        forecastedDates = self.getDatesIntoFuture(s)
        
        # print(forecasted)
        # print(forecastedDates)
        
        # Creating Data Frame to contain the predicted prices
        forecastedPrices = pd.DataFrame({'date': forecastedDates, 'adjClose': forecasted})
        
        # Remove time from date columns
        realizedPrices['date'] = realizedPrices['date'].dt.date
        forecastedPrices['date'] = forecastedPrices['date'].dt.date
        
        # Organize data into a dictionary to be consumed
        combinedPrices = {'realized': {'date': realizedPrices['date'].tolist(), 'prices': realizedPrices['close'].tolist()},
                        'forecasted': {'date': forecastedPrices['date'].tolist(), 'prices': forecastedPrices['close'].tolist()}}
        
        return combinedPrices
    
    # Get dates so many days into the future
    # TODO: Replace to consider actual trading days
    def getDatesIntoFuture(self, s):
        lastDate = self.stock.getFinalRealizedDate()
        
        dates = []
        
        for i in range(1, s + 1):
            dates.append(lastDate + pd.DateOffset(days=i))
        
        return dates
    
    def predictIntoFuture(self, s):
        # For forecasted values only
        predictedNormalizedPrices = []

        # Using look-back amount to append to normalized dataset and using forecasted data to predict future forecasted values
        # Note that this will cause larger errors, but is needed to perform real forecasts
        for day in range(s):
            # Merging together the predicted and actual prices to use in future forecasts, if there are some predictions made
            if len(predictedNormalizedPrices) != 0:
                npPredicted = np.reshape(np.array(predictedNormalizedPrices), (-1, 1))    
                combinedPrices = np.concatenate((self.normalizedPrices, npPredicted))
            else:
                combinedPrices = self.normalizedPrices
            
            # Taking the past amount of values, specified by the lookback amount. This will be used in the model predictions.
            X = np.reshape(combinedPrices[-self.lookBack:], (-1, 1, self.lookBack))
            
            # Obtaining predicted price and adding it to the predicted prices array to be used in future forecasts (depending on lookback amount)
            predictedPrice = self.model.predict(X)[0][0]
            
            predictedNormalizedPrices.append(predictedPrice)
            
        predictedPrices = self.scaler.inverse_transform(np.reshape(predictedNormalizedPrices, (-1, 1)))
            
        return predictedPrices
        
# Class manual testing code
if __name__ == "__main__":
    forecaster = LSTMForecaster("C", "2010-01-01")
    forecaster.createModel(8)
    
    # Getting forecasted values for 5 days ahead
    print(forecaster.getCombinedPrices(5))