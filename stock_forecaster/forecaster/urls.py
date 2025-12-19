from django.urls import path
from . import views

urlpatterns = [
    path('lstmForecast/', views.lstmForecast, name='lstmForecast'),
    path('stockDetail/<stockTicker>/', views.stockDetail, name='stockDetail'),
    path('max-start-date/<look_back>/', views.max_start_date, name="max-start-date")
]