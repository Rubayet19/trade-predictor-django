import joblib
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
import os
import logging
from financial_data.models import StockData
from django.db import transaction
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class StockPredictor:
    def __init__(self, symbol):
        self.symbol = symbol
        self.model = None
        self.scaler = None
        self._load_model()

    def _load_model(self):
        try:
            model_path = os.path.join(settings.BASE_DIR, 'financial_data', 'ml_models', f'{self.symbol}_model.pkl')
            scaler_path = os.path.join(settings.BASE_DIR, 'financial_data', 'ml_models', f'{self.symbol}_scaler.pkl')

            cache_key = f'ml_model_{self.symbol}'
            cached_model = cache.get(cache_key)

            if cached_model:
                self.model, self.scaler = cached_model
            else:
                self.model = joblib.load(model_path)
                self.scaler = joblib.load(scaler_path)
                cache.set(cache_key, (self.model, self.scaler), timeout=3600)

        except FileNotFoundError:
            raise ValidationError(f"No trained model available for symbol {self.symbol}")
        except Exception as e:
            logger.error(f"Error loading model for {self.symbol}: {str(e)}")
            raise ValidationError(f"Error loading model: {str(e)}")

    def _prepare_features(self, data):
        features = ['open_price', 'high_price', 'low_price', 'close_price', 'volume']
        X = data[features]
        return pd.DataFrame(self.scaler.transform(X), columns=features)

    def _get_historical_data(self, days=60):
        cutoff_date = datetime.now().date() - timedelta(days=days)
        data = StockData.objects.filter(
            symbol=self.symbol,
            date__gte=cutoff_date
        ).order_by('-date')

        if not data.exists():
            raise ValidationError(f"Insufficient historical data for {self.symbol}")

        return pd.DataFrame(list(data.values()))

    @transaction.atomic
    def predict_next_30_days(self):
        try:
            historical_data = self._get_historical_data()
            if len(historical_data) < 30:
                raise ValidationError(f"Insufficient historical data for {self.symbol}")

            last_known_data = historical_data.iloc[0]
            current_date = last_known_data['date']
            predictions = []

            current_features = self._prepare_features(pd.DataFrame([last_known_data]))

            for i in range(30):
                target_date = current_date + timedelta(days=i + 1)

                predicted_price = self.model.predict(current_features)[0]

                # Store prediction in database
                stock_data, created = StockData.objects.update_or_create(
                    symbol=self.symbol,
                    date=target_date,
                    defaults={
                        'predicted_price': round(float(predicted_price), 2),
                        'open_price': last_known_data['open_price'],
                        'close_price': last_known_data['close_price'],
                        'high_price': last_known_data['high_price'],
                        'low_price': last_known_data['low_price'],
                        'volume': last_known_data['volume']
                    }
                )

                predictions.append({
                    'date': target_date,
                    'predicted_price': round(float(predicted_price), 2)
                })

                # Update features for next prediction
                last_known_data = {
                    'open_price': predicted_price,
                    'high_price': predicted_price * 1.01,
                    'low_price': predicted_price * 0.99,
                    'close_price': predicted_price,
                    'volume': last_known_data['volume']
                }
                current_features = self._prepare_features(pd.DataFrame([last_known_data]))

            return predictions

        except Exception as e:
            logger.error(f"Error making predictions for {self.symbol}: {str(e)}")
            raise ValidationError(f"Error making predictions: {str(e)}")