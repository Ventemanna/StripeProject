from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.PaymentTemplates.as_view(), name='home'),
    path('create-checkout-session', views.CreateCheckoutSession.as_view(), name='create-checkout-session'),
    path('cat', views.cat, name='cat'),
]