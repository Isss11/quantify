from django.shortcuts import render
from django.http import HttpResponse
from . import LSTMForecaster, StockDetail, MaxStartDate
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from rest_framework.decorators import api_view

@api_view(['POST'])
def lstmForecast(request):
    requestValues = JSONParser().parse(request)
    
    # Creating model with given look-back amount
    forecaster = LSTMForecaster.LSTMForecaster(requestValues["ticker"], requestValues["sampleStartDate"])
    forecaster.create_model(requestValues["lookBack"], requestValues["epochs"], requestValues["batchSize"])
    
    # Getting prices and model accuracy details to include in response
    prices = forecaster.get_combined_prices(requestValues['forecastLength'])
    modelAccuracy, modelDetails = forecaster.calc_model_accuracy()
    modelParameters = {"modelType": "LSTM", "stock": requestValues["ticker"], "forecastLength": requestValues["forecastLength"], "lookBack": requestValues["lookBack"], "epochs": requestValues["epochs"], "batchSize": requestValues["batchSize"]}
    
    response = dict({"parameters": modelParameters, "details": modelDetails, "prices": prices, "modelAccuracy": modelAccuracy})
    
    return JsonResponse(response)
    

# Returns general stock information used in the UI
@api_view(['POST'])
def stockDetail(request, stockTicker):
    stockInfo = StockDetail.StockDetail(str(stockTicker))
    
    return JsonResponse(stockInfo.getGeneralInfo())

@api_view(['POST'])
def max_start_date(request, look_back): 
    start_date = MaxStartDate.get_max_start_date(int(look_back))
       
    return JsonResponse({"max_start_date": start_date})