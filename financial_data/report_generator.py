import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from .models import StockData
from .backtesting import backtest_strategy
from .ml_integration import StockPredictor
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib.units import inch
from PIL import Image as PILImage


def generate_report(symbol, start_date, end_date, initial_investment, buy_ma_window, sell_ma_window):

    stock_data = StockData.objects.filter(symbol=symbol, date__range=[start_date, end_date]).order_by('date')

    if not stock_data.exists():
        raise ValueError(f"No stock data available for {symbol} between {start_date} and {end_date}")


    backtest_results = backtest_strategy(symbol, initial_investment, buy_ma_window, sell_ma_window)


    predictor = StockPredictor(symbol)
    predictions = predictor.predict_next_30_days()

    # Calculate key metrics
    final_value = backtest_results.get('final_value', initial_investment)
    total_return = final_value - initial_investment
    roi = (total_return / initial_investment) * 100


    fig, ax = plt.subplots(figsize=(10, 6))

    # Actual vs Predicted Prices
    dates = [d.date for d in stock_data]
    actual_prices = [float(d.close_price) for d in stock_data if float(d.close_price) > 0]
    actual_dates = [d.date for d in stock_data if float(d.close_price) > 0]
    predicted_prices = [float(d.predicted_price) for d in stock_data if d.predicted_price is not None]
    predicted_dates = [d.date for d in stock_data if d.predicted_price is not None]

    if actual_prices:
        ax.plot(actual_dates, actual_prices, label='Actual')
    if predicted_prices:
        ax.plot(predicted_dates, predicted_prices, label='Predicted')

    ax.set_title(f'{symbol} - Actual vs Predicted Prices')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    ax.legend()


    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close(fig)


    report_data = {
        'symbol': symbol,
        'start_date': start_date,
        'end_date': end_date,
        'initial_investment': initial_investment,
        'final_portfolio_value': final_value,
        'total_return': total_return,
        'roi': roi,
        'predictions': predictions
    }

    return report_data, buf


def generate_pdf_report(report_data, plot_buffer):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []


    elements.append(Paragraph(f"Financial Report for {report_data['symbol']}", styles['Title']))
    elements.append(Spacer(1, 12))

    # Key Metrics Table
    data = [
        ['Metric', 'Value'],
        ['Initial Investment', f"${report_data['initial_investment']:,.2f}"],
        ['Final Portfolio Value', f"${report_data['final_portfolio_value']:,.2f}"],
        ['Total Return', f"${report_data['total_return']:,.2f}"],
        ['ROI', f"{report_data['roi']:.2f}%"],
    ]

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))


    elements.append(Paragraph("Price Visualization", styles['Heading2']))
    elements.append(Spacer(1, 12))


    plot_buffer.seek(0)
    img = PILImage.open(plot_buffer)
    img_width = 6 * inch
    img_height = 4 * inch
    img_path = f"/tmp/{report_data['symbol']}_plot.png"
    img.save(img_path, format='PNG')

    elements.append(Image(img_path, width=img_width, height=img_height))


    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    # Clean up temporary image file
    import os
    os.remove(img_path)

    return pdf

