from django.core.exceptions import ValidationError
from .models import StockData
import pandas as pd
from django.core.cache import cache
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

def calculate_moving_average(data, window):
    return data['close_price'].rolling(window=window).mean()

def validate_backtest_params(symbol, initial_investment, buy_ma_window, sell_ma_window):
    if not isinstance(symbol, str) or len(symbol) == 0:
        raise ValidationError("Symbol must be a non-empty string")
    if not isinstance(initial_investment, (int, float, Decimal)) or initial_investment <= 0:
        raise ValidationError("Initial investment must be a positive number")
    if not isinstance(buy_ma_window, int) or buy_ma_window <= 0:
        raise ValidationError("Buy MA window must be a positive integer")
    if not isinstance(sell_ma_window, int) or sell_ma_window <= 0:
        raise ValidationError("Sell MA window must be a positive integer")

def get_stock_data(symbol):
    cache_key = f'stock_data_{symbol}'
    data = cache.get(cache_key)
    if data is None:
        data = StockData.objects.filter(symbol=symbol).order_by('date').values('date', 'close_price')
        if not data:
            raise ValidationError(f"No data available for symbol {symbol}")
        cache.set(cache_key, list(data), timeout=3600)  # Cache for 1 hour
    return pd.DataFrame(data)

def backtest_strategy(symbol, initial_investment, buy_ma_window, sell_ma_window):
    logger.info(f"Starting backtest for {symbol} with initial investment {initial_investment}")
    validate_backtest_params(symbol, initial_investment, buy_ma_window, sell_ma_window)

    df = get_stock_data(symbol)
    df['close_price'] = df['close_price'].astype(float)  # Convert to float for calculations

    if (df['close_price'] <= 0).any():
        logger.warning(f"Zero or negative prices found for {symbol}. Removing these entries.")
        df = df[df['close_price'] > 0]

    df['buy_ma'] = calculate_moving_average(df, buy_ma_window)
    df['sell_ma'] = calculate_moving_average(df, sell_ma_window)

    cash = float(initial_investment)
    shares = 0
    trades = 0
    max_drawdown = 0
    peak_value = float(initial_investment)
    transaction_history = []

    for i, row in df.iterrows():
        if i < max(buy_ma_window, sell_ma_window):
            continue

        portfolio_value = cash + shares * row['close_price']

        if portfolio_value > peak_value:
            peak_value = portfolio_value
        else:
            drawdown = (peak_value - portfolio_value) / peak_value
            max_drawdown = max(max_drawdown, drawdown)


        if row['close_price'] < row['buy_ma'] and cash > 0:
            shares_to_buy = cash // row['close_price']
            if shares_to_buy > 0:
                cash -= shares_to_buy * row['close_price']
                shares += shares_to_buy
                trades += 1
                transaction_history.append({
                    'date': row['date'].isoformat(),
                    'action': 'buy',
                    'price': float(row['close_price']),
                    'shares': int(shares_to_buy),
                    'value': float(shares_to_buy * row['close_price'])
                })


        elif row['close_price'] > row['sell_ma'] and shares > 0:
            sell_value = shares * row['close_price']
            cash += sell_value
            transaction_history.append({
                'date': row['date'].isoformat(),
                'action': 'sell',
                'price': float(row['close_price']),
                'shares': int(shares),
                'value': float(sell_value)
            })
            shares = 0
            trades += 1

    final_value = cash + shares * df.iloc[-1]['close_price']
    total_return = (final_value - float(initial_investment)) / float(initial_investment)

    logger.info(f"Backtest completed for {symbol}. Total return: {total_return:.2%}")

    return {
        'total_return': float(total_return),
        'max_drawdown': float(max_drawdown),
        'trades_executed': trades,
        'final_value': float(final_value),
        'transaction_history': transaction_history
    }