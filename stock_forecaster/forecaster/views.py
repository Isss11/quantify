from django.shortcuts import render
from django.http import HttpResponse
from . import LSTMForecaster, StockDetail
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework.decorators import api_view
from rest_framework import status

@api_view(['POST'])
def lstmForecast(request):
    requestValues = JSONParser().parse(request)
    
    # Creating model with given look-back amount
    forecaster = LSTMForecaster.LSTMForecaster(requestValues["ticker"], requestValues["sampleStartDate"])
    forecaster.createModel(requestValues["lookBack"], requestValues["epochs"], requestValues["batchSize"])
    
    # Getting prices and model accuracy details to include in response
    prices = forecaster.getCombinedPrices(requestValues['forecastLength'])
    modelAccuracy, modelDetails = forecaster.getModelAccuracy()
    modelParameters = {"modelType": "LSTM", "stock": requestValues["ticker"], "forecastLength": requestValues["forecastLength"], "lookBack": requestValues["lookBack"], "epochs": requestValues["epochs"], "batchSize": requestValues["batchSize"]}
    
    response = dict({"parameters": modelParameters, "details": modelDetails, "prices": prices, "modelAccuracy": modelAccuracy})
    
    return JsonResponse(response)
    

# Returns general stock information used in the UI
@api_view(['POST'])
def stockDetail(request, stockTicker):
    stockInfo = StockDetail.StockDetail(str(stockTicker))
    
    return JsonResponse(stockInfo.getGeneralInfo())