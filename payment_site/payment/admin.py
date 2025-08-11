from django.contrib import admin
from .models import Items, Orders, Discounts, Tax

class ItemAdmin(admin.ModelAdmin):
    list_display = ['name','price', 'currency']
    ordering = ['name', 'price']

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'total_price','is_paid']
    ordering = ['-id', '-is_paid']

class DiscountAdmin(admin.ModelAdmin):
    list_display = ['name', 'percent_off', 'duration', 'active']
    ordering = ['name', '-percent_off', '-active']
    exclude = ('stripe_coupon_id',)

class TaxAdmin(admin.ModelAdmin):
    list_display = ['name', 'percent']
    exclude = ('stripe_tax_id',)

admin.site.register(Items, ItemAdmin)
admin.site.register(Orders, OrderAdmin)
admin.site.register(Discounts, DiscountAdmin)
admin.site.register(Tax, TaxAdmin)