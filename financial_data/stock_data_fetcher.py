import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from django.db import transaction
from .models import StockData
import logging

load_dotenv()

logger = logging.getLogger(__name__)

API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
BASE_URL = 'https://www.alphavantage.co/query'


def fetch_stock_data(symbol, start_date, end_date):
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'apikey': API_KEY
    }

    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'Note' in data:
                # Alpha Vantage returns a 'Note' key when rate limit is hit
                logger.warning(f"Rate limit hit for {symbol}. Waiting before retry.")
                time.sleep(60)
                continue

            if 'Time Series (Daily)' not in data:
                logger.error(f"Invalid response from Alpha Vantage for symbol {symbol}")
                return

            daily_data = data['Time Series (Daily)']

            stock_data_list = []
            for date_str, values in daily_data.items():
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                if start_date <= date <= end_date:
                    stock_data_list.append(
                        StockData(
                            symbol=symbol,
                            date=date,
                            open_price=float(values['1. open']),
                            high_price=float(values['2. high']),
                            low_price=float(values['3. low']),
                            close_price=float(values['4. close']),
                            volume=int(values['5. volume'])
                        )
                    )

            with transaction.atomic():
                StockData.objects.bulk_create(
                    stock_data_list,
                    update_conflicts=True,
                    update_fields=['open_price', 'high_price', 'low_price', 'close_price', 'volume'],
                    unique_fields=['symbol', 'date']
                )

            logger.info(f"Successfully fetched and stored data for {symbol}")
            return

        except requests.Timeout:
            logger.error(f"Timeout occurred while fetching data for {symbol}")
        except requests.RequestException as e:
            logger.error(f"Network error occurred for {symbol}: {e}")
        except ValueError as e:
            logger.error(f"Error processing data for {symbol}: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred for {symbol}: {e}")

        if attempt < max_retries - 1:
            wait_time = 2 ** attempt
            logger.info(f"Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
        else:
            logger.error(f"Failed to fetch data for {symbol} after {max_retries} attempts")
            break


