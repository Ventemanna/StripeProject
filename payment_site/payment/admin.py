from django.contrib import admin
from .models import Items, Orders, Discounts, Tax

admin.site.register(Items)
admin.site.register(Orders)
admin.site.register(Discounts)
admin.site.register(Tax)