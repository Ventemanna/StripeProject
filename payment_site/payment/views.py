import os
import uuid

import stripe
from django.db.models import Prefetch
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from .models import Items, Orders, ItemOrder
from .forms import ItemForm

from django.conf import settings

stripe.api_key = settings.SECRET_STRIPE_KEY

def home_page(request):
    form = ItemForm()
    all_items = Items.objects.all()
    info_data = {
        "all_items": all_items,
        "item_form": form,
    }
    return render(request, 'home.html', info_data)

def get_item_id(request, item_id):
    item = Items.objects.get(id=item_id)
    form = ItemForm()
    context = {
        'form': form,
        'item': item,
        'public_stripe_key': settings.PUBLIC_STRIPE_KEY,
    }
    return render(request, 'about_item.html', context)

def get_order(request):
    if 'order_id' in request.session:
        order = Orders.objects.get(id=request.session['order_id'])
    else:
        order = Orders.objects.create(total_price=0)
        order.save()
        request.session['order_id'] = order.id
    return order

def create_new_order(request, item_id):
    item = Items.objects.get(id=item_id)
    form = ItemForm(request.POST or None)
    quantity = 1
    if request.method == 'POST':
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
    order = Orders.objects.create(total_price=0)
    order_item = ItemOrder(order=order, item=item, quantity=quantity)
    order_item.save()
    order.total_price += item.price * quantity
    order.save()
    return redirect('buy', order_id=order.id)

def buy_item(request, item_id):
    try:
        item = Items.objects.get(id=item_id)
        line_items = [{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': item.name,
                    'description': item.description,
                },
                'unit_amount': int(item.price * 100)
            },
            'quantity': 1,
        }]
        session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url='http://127.0.0.1:8000/success',
            cancel_url='http://127.0.0.1:8000/cart',
        )
        return JsonResponse({'id': session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)

def success(request):
    if 'order_id' in request.session:
        order_id = request.session['order_id']
        item_order = ItemOrder.objects.filter(order=order_id)
        item_order.delete()
        request.session.pop('order_id')
    return render(request, 'success_payment.html')

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

        order = get_order(request)
        order.total_price += item.price * quantity
        order.save()

        item_order, is_created = ItemOrder.objects.get_or_create(
            item=item,
            order=order
        )
        if not is_created:
            item_order.quantity += quantity
        else:
            item_order.quantity = quantity
        item_order.save()
    return redirect('/')

def cart(request):
    context = {}
    if 'order_id' in request.session:
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
        order = get_order(request)
        context['total_price'] = order.total_price
        context['order_id'] = order.id
    return render(request,'cart.html', context)

def clear_cart(request):
    if 'order_id' in request.session:
        order_id = request.session['order_id']
        order = Orders.objects.get(id=order_id)
        order.total_price = 0
        order.save()
        item_orders = ItemOrder.objects.filter(order=order_id)
        item_orders.delete()
    return redirect('/')

def error(request):
    return render(request, 'error.html')