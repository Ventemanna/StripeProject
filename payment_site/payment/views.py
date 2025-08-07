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

def cat(request):
    return HttpResponse("Meow.")

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

def get_item_id(request, id):
    pass

def get_buy_id(request, id):
    pass

def cancel(request):
    return HttpResponse("Cancel.")

def success(request):
    return HttpResponse("Success.")

def add_to_cart(request, item_id):
    #TODO: добавить возможность добавлять количество добавляемого товара
    item = Items.objects.get(id=item_id)
    if 'order_id' in request.session:
        order = Orders.objects.get(id=request.session['order_id'])
    else:
        order = Orders.objects.create(total_price=0)
        order.save()
        request.session['order_id'] = order.id
    order.item.add(item)
    return redirect('home')

def cart(request):
    order_id = request.session['order_id']
    order_items = ItemOrder.objects.filter(order=order_id)
    info_data = []
    for item in order_items:
        info_data.append({
            'id': item.item.id,
            'name': item.item.name,
            'description': item.item.description,
            'price': item.item.price,
            'quantity': item.quantity,
        })
    context = {'items': info_data}
    return render(request,'cart.html', context)