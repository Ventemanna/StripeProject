from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('create_checkout_session', views.create_checkout_session, name='create-checkout-session'),
    path('buy/<int:order_id>', views.get_buy_id, name='buy'),
    path('item/<int:item_id>', views.get_item_id, name='item'),
    path('process_item/<int:item_id>', views.process_item, name='process_item'),
    path('add_item/<int:item_id>', views.add_to_cart, name='add_item'),
    path('cancel', views.cancel, name='cancel'),
    path('success', views.success, name='success'),
    path('cart', views.cart, name='cart'),
    path('clear_cart', views.clear_cart, name='delete_from_cart'),
    path('error', views.error, name='error'),
]