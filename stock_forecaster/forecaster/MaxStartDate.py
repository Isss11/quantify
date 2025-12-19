from datetime import date, timedelta
from .LSTMForecaster import TRAIN_PROPORTION

# Used to increase offset relative to 2 weekend days, and 1 potential holiday
WEEKEND_HOLIDAY_MULTIPLIER = 10/7

def get_max_start_date(look_back):
    cur_date = date.today()
    offset_days = int(((2 + look_back)/(1 - TRAIN_PROPORTION)) * WEEKEND_HOLIDAY_MULTIPLIER)

    latest_start_date = cur_date - timedelta(days=offset_days)
    
    return latest_start_date