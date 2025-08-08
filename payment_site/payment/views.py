import os
import uuid

import stripe
from django.db.models import Prefetch
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Items, Orders, ItemOrder
from .forms import ItemForm

from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv('SECRET_API_KEY')

def home_page(request):
    form = ItemForm()
    all_items = Items.objects.all()
    info_data = {
        "all_items": all_items,
        "item_form": form,
    }
    return render(request, 'home.html', info_data)

#TODO: поменять чтобы в line_items была информация про наши предметы
def create_checkout_session(request):
    session = stripe.checkout.Session.create (
        line_items=[{
            'price_data': {
                'currency': 'rub',
                'product_data': {
                    'name': 'T-shirt',
                },
                'unit_amount': 1350
            },
            'quantity': 3,
        }],
        mode='payment',
        success_url='http://localhost/success',
        cancel_url='http://localhost/cancel',
    )
    return redirect(session.url, code=303)

def get_item_id(request, item_id):
    item = Items.objects.get(id=item_id)
    form = ItemForm(request.POST or None)
    quantity = 1
    if request.method == 'POST':
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
    context = {
        'item': item,
        'quantity': quantity,
    }
    return render(request, 'about_item.html', context)

def get_buy_id(request, order_id):
    pass

def cancel(request):
    return HttpResponse("Cancel.")

def success(request):
    return HttpResponse("Success.")

def process_item(request, item_id):
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            if request.POST.get('action') == 'add_to_cart':
                return redirect(f'../../add_item/{item_id}')
            elif request.POST.get('action') == 'buy_now':
                return redirect(f'../item/{item_id}')

def add_to_cart(request, item_id):
    form = ItemForm(request.POST or None)
    quantity = 1
    if request.method == "POST":
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
        try:
            item = Items.objects.get(id=item_id)
        except Items.DoesNotExist:
            return redirect('error')
        if 'order_id' in request.session:
            order = Orders.objects.get(id=request.session['order_id'])
        else:
            order = Orders.objects.create(total_price=0)
            order.save()
            request.session['order_id'] = order.id

        item_order, is_created = ItemOrder.objects.get_or_create(
            item=item,
            order=order
        )
        if not is_created:
            item_order.quantity += quantity
        else:
            item_order.quantity = quantity
        item_order.save()
    return redirect('home')

def cart(request):
    order_id = request.session['order_id']
    item_orders = ItemOrder.objects.filter(order=order_id)
    info_data = []
    for item_order in item_orders:
        info_data.append({
            'id': item_order.item.id,
            'name': item_order.item.name,
            'description': item_order.item.description,
            'price': item_order.item.price,
            'quantity': item_order.quantity,
        })
    context = {'items': info_data}
    return render(request,'cart.html', context)

def clear_cart(request):
    order_id = request.session['order_id']
    item_orders = ItemOrder.objects.filter(order=order_id)
    item_orders.delete()
    return redirect('cart')

def error(request):
    return render(request, 'error.html')