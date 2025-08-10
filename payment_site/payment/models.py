import decimal

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
import stripe

class Items(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'

    def __str__(self):
        return f"{self.name}. За {self.price}"

class Discounts(models.Model):
    duration_of_coupon = [
        ('forever', 'Навсегда'),
        ('once', 'Единожды'),
        ('repeating', 'Повторяемый')
    ]
    name = models.CharField(max_length=100)
    percent_off = models.FloatField(default=1.0, validators=[MinValueValidator(1), MaxValueValidator(100)])
    duration = models.CharField(max_length=10, choices=duration_of_coupon, default='once')

    stripe_coupon_id = models.CharField(max_length=100, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"Скидка под названием '{self.name}' на {self.percent_off}%"

    def save(self, *args, **kwargs):
        if not self.stripe_coupon_id:
            coupon = stripe.Coupon.create(
                duration=self.duration,
                percent_off=self.percent_off,
                duration_in_months=3 if self.duration == 'repeating' else None,
                max_redemptions=1 if self.duration == 'once' else None,
            )
            self.stripe_coupon_id = coupon.id
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Discount'
        verbose_name_plural = 'Discounts'

class Tax(models.Model):
    name = models.CharField(max_length=100)
    percent = models.FloatField(default=1.0, validators=[MinValueValidator(1), MaxValueValidator(100)])
    stripe_tax_id = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    def save(self, *args, **kwargs):
        if not self.stripe_tax_id:
            tax  = stripe.TaxRate.create(
                display_name=self.name,
                percentage=self.percent,
                inclusive=False,
            )
            self.stripe_tax_id = tax.id
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Tax'
        verbose_name_plural = 'Taxes'

class Orders(models.Model):
    paid_values = [
        ('paid', 'Оплачен'),
        ('cancelled', 'Отменен'),
        ('created', 'Создан')
    ]

    item = models.ManyToManyField(Items)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.OneToOneField(Discounts, on_delete=models.PROTECT, null=True, blank=True)
    tax = models.ManyToManyField(Tax)

    is_paid = models.CharField(max_length=10, choices=paid_values, default='created')

    def __str__(self):
        return f"Заказ {self.id}"

    def calculate_total_price(self):
        order = Orders.objects.get(id=self.id)
        total_price = sum([item.price for item in order.item.all()])
        tax = 0
        discount = 0
        if order.discount:
            discount = total_price * (decimal.Decimal(order.discount.percent_off) / 100)
        total_price -= discount
        if order.tax:
            tax_percent = 0
            for tax in order.tax.all():
                tax_percent += tax.percent
            tax = total_price * (decimal.Decimal(tax_percent) / 100)
        self.total_price = round(total_price + tax, 2)
        self.save()

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'