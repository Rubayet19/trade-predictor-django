from django.urls import path
from .views import run_backtest, predict_stock_prices, get_report

urlpatterns = [
    path('backtest/', run_backtest, name='run_backtest'),
    path('predict/', predict_stock_prices, name='predict_stock_prices'),
    path('report/', get_report, name='get_report'),
]