from django.core.management.base import BaseCommand
from django.utils import timezone
from financial_data.stock_data_fetcher import fetch_stock_data
from datetime import timedelta


class Command(BaseCommand):
    help = 'Fetches stock data for a given symbol and date range'

    def add_arguments(self, parser):
        parser.add_argument('symbol', type=str, help='Stock symbol (e.g., IBM)')
        parser.add_argument('--days', type=int, default=1, help='Number of days to fetch (default: 30)')
        parser.add_argument('--years', type=int, default=0, help='Number of years to fetch (default: 0)')

    def handle(self, *args, **options):
        symbol = options['symbol'].upper()
        years = options['years']
        days = options['days']

        if years < 0 or days < 0:
            self.stderr.write(self.style.ERROR('Years and days must be non-negative integers'))
            return
        if years == 0 and days == 0:
            self.stderr.write(self.style.ERROR('You must specify either --years or --days or both'))
            return

        end_date = timezone.now().date()
        start_date = end_date


        if years > 0:
            try:
                start_date = start_date.replace(year=start_date.year - years)
            except ValueError:
                # Handle leap year case if the current day doesn't exist in the previous year
                start_date = start_date - timedelta(days=365 * years)

        if days > 0:
            start_date -= timedelta(days=days)

        self.stdout.write(f"Fetching data for {symbol} from {start_date} to {end_date}")
        fetch_stock_data(symbol, start_date, end_date)
        self.stdout.write(self.style.SUCCESS('Data fetching completed'))