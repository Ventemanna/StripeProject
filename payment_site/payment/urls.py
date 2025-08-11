from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('create_new_order/<int:item_id>', views.create_one_time_order, name='create_new_order'),
    path('buy/<int:item_id>', views.buy_item, name='buy-item'),
    path('buy_order/<int:order_id>', views.buy_order, name='buy-order'),
    path('item/<int:item_id>', views.get_item_id, name='item'),
    path('add_item/<int:item_id>', views.add_to_cart, name='add_item'),
    path('success', views.success, name='success'),
    path('cancel', views.cancel_order, name='cancel'),
    path('clear_cart', views.clear_cart, name='delete_from_cart'),
    path('undefined', views.undefined, name='undefined'),
    path('error', views.error, name='error'),
    path('cart', views.cart, name='cart'),
    path('add_discount/<str:name_coupon>', views.add_discount, name='add-discount')
]