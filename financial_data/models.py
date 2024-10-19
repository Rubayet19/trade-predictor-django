from django.db import models
from django.core.validators import MinValueValidator

class StockData(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    open_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    close_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    high_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    low_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    volume = models.BigIntegerField(validators=[MinValueValidator(0)])
    predicted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('symbol', 'date')
        indexes = [
            models.Index(fields=['symbol', 'date']),
        ]

    def __str__(self):
        return f"{self.symbol} - {self.date}"
