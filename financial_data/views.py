import traceback

from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.conf import settings
import json
import io
from reportlab.pdfgen import canvas

from .backtesting import backtest_strategy
from .ml_integration import StockPredictor
from django.core.cache import cache
import logging
from datetime import datetime
from .report_generator import generate_report, generate_pdf_report

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def run_backtest(request):
    try:
        data = json.loads(request.body)
        symbol = data['symbol']
        initial_investment = float(data['initial_investment'])
        buy_ma_window = int(data['buy_ma_window'])
        sell_ma_window = int(data['sell_ma_window'])

        logger.info(f"Received backtest request for {symbol}")

        cache_key = f'backtest_{symbol}_{initial_investment}_{buy_ma_window}_{sell_ma_window}'
        results = cache.get(cache_key)

        if results is None:
            results = backtest_strategy(symbol, initial_investment, buy_ma_window, sell_ma_window)
            cache.set(cache_key, results, timeout=3600)  # Cache for 1 hour
        else:
            logger.info(f"Cache hit for backtest of {symbol}")

        return JsonResponse(results)
    except KeyError as e:
        logger.error(f"Missing required parameter: {str(e)}")
        return JsonResponse({'error': f'Missing required parameter: {str(e)}'}, status=400)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.exception("Unexpected error occurred during backtest")
        if settings.DEBUG:
            return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def predict_stock_prices(request):
    try:
        data = json.loads(request.body)
        symbol = data.get('symbol')

        if not symbol:
            return JsonResponse({'error': 'Symbol is required'}, status=400)

        logger.info(f"Received prediction request for {symbol}")

        cache_key = f'prediction_{symbol}'
        predictions = cache.get(cache_key)

        if predictions is None:
            predictor = StockPredictor(symbol)
            predictions = predictor.predict_next_30_days()
            cache.set(cache_key, predictions, timeout=3600)  # Cache for 1 hour
        else:
            logger.info(f"Cache hit for prediction of {symbol}")

        response_data = {
            'symbol': symbol,
            'predictions': [
                {
                    'date': pred['date'].isoformat(),
                    'predicted_price': pred['predicted_price']
                }
                for pred in predictions
            ]
        }

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.exception(f"Unexpected error during prediction for {symbol}")
        if settings.DEBUG:
            return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def get_report(request):
    try:
        data = json.loads(request.body)
        symbol = data['symbol']
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        initial_investment = float(data['initial_investment'])
        buy_ma_window = int(data['buy_ma_window'])
        sell_ma_window = int(data['sell_ma_window'])
        report_format = data.get('format', 'json')

        report_data, plot_buffer = generate_report(symbol, start_date, end_date, initial_investment, buy_ma_window,
                                                   sell_ma_window)

        if report_format == 'pdf':
            pdf = generate_pdf_report(report_data, plot_buffer)
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{symbol}_report.pdf"'
        else:
            response = JsonResponse(report_data)

        return response

    except Exception as e:
        logger.exception(f"Error during report generation for {symbol if 'symbol' in locals() else 'unknown symbol'}")
        error_message = f"Error: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"

        if report_format == 'pdf':
            buffer = io.BytesIO()
            p = canvas.Canvas(buffer)
            y = 750
            for line in error_message.split('\n'):
                p.drawString(50, y, line)
                y -= 15
                if y < 50:
                    p.showPage()
                    y = 750
            p.showPage()
            p.save()
            buffer.seek(0)
            return HttpResponse(buffer.getvalue(), content_type='application/pdf')
        else:
            return JsonResponse({'error': str(e)}, status=500)