from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('cat', views.cat, name='cat'),
    path('create_checkout_session', views.create_checkout_session, name='create-checkout-session'),
    path('buy/<int:id>', views.get_buy_id, name='buy'),
    path('item/<int:id>', views.get_item_id, name='item'),
    path('cancel', views.cancel, name='cancel'),
    path('success', views.success, name='success'),
    path('add_item/<int:item_id>', views.add_to_cart, name='add_item'),
    path('cart', views.cart, name='cart'),
]