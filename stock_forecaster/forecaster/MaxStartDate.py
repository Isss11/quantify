from datetime import date, timedelta
from .LSTMForecaster import TRAIN_PROPORTION

def get_max_start_date(look_back):
    cur_date = date.today()
    offset_days = int((2 + look_back)/(1 - TRAIN_PROPORTION))

    latest_start_date = cur_date - timedelta(days=offset_days)
    
    return latest_start_date