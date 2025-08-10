import decimal

import stripe
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Items, Orders, Discounts, Tax

from django.conf import settings

stripe.api_key = settings.SECRET_STRIPE_KEY

def home_page(request):
    order = get_order(request)
    all_items = Items.objects.all()
    info_data = {
        "all_items": all_items,
    }
    return render(request, 'home.html', info_data)

def get_item_id(request, item_id):
    item = Items.objects.get(id=item_id)
    context = {
        'item': item,
        'public_stripe_key': settings.PUBLIC_STRIPE_KEY,
    }
    return render(request, 'about_item.html', context)

def get_order(request):
    if 'order_id' in request.session:
        try:
            order = Orders.objects.get(id=request.session['order_id'])
        except Orders.DoesNotExist:
            request.session.pop('order_id')
    else:
        order = Orders.objects.create(total_price=0)
        order.save()
        request.session['order_id'] = order.id
    return order

def create_one_time_order(request, item_id):
    item = Items.objects.get(id=item_id)
    order = Orders.objects.create(total_price=item.price)
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
            cancel_url='http://127.0.0.1:8000/cancel',
        )
        return JsonResponse({'id': session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)

def cancel_order(request):
    order = get_order(request)
    order.is_paid = 'cancelled'
    order.save()
    return redirect('delete_from_cart')

def buy_order(request, order_id):
    try:
        order = get_order(request)
        line_items = []
        discount = order.discount.stripe_coupon_id if order.discount else None
        tax = []
        for el in order.tax.all():
            tax.append(el.stripe_tax_id)
        for item in order.item.all():
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.name,
                        'description': item.description,
                    },
                    'unit_amount': int(item.price * 100)
                },
                'quantity': 1,
                'tax_rates': tax
            })
        session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url='http://127.0.0.1:8000/success',
            cancel_url='http://127.0.0.1:8000/cart',
            discounts=[{"coupon": discount}],
        )
        return JsonResponse({'id': session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)

def success(request):
    if 'order_id' in request.session:
        order = get_order(request)
        order.is_paid = 'paid'
        request.session.pop('order_id')
    return render(request, 'success_payment.html')

def add_to_cart(request, item_id):
    try:
        item = Items.objects.get(id=item_id)
    except Items.DoesNotExist:
        return redirect('error')
    order = get_order(request)
    if not order.item.filter(id=item_id).exists():
        order.item.add(item)
        order.total_price += item.price
        order.save()
    return redirect('/')

def cart(request):
    context = {}
    if 'order_id' in request.session:
        item_orders = get_order(request)
        info_data = []
        for item in item_orders.item.all():
            info_data.append({
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'price': item.price,
            })
        context = {'items': info_data}
        order = get_order(request)
        order.calculate_total_price()
        context['public_stripe_key'] = settings.PUBLIC_STRIPE_KEY
        context['total_price'] = order.total_price
        context['order_id'] = order.id
    return render(request,'cart.html', context)

def clear_cart(request):
    if 'order_id' in request.session:
        order_id = request.session['order_id']
        order = Orders.objects.get(id=order_id)
        order.item.clear()
        order.discount = None
        order.tax.clear()
        order.total_price = 0
        order.save()
    return redirect('/')

def error(request):
    return render(request, 'error.html')

def add_discount(request, name_coupon):
    order = get_order(request)
    try:
        coupon = Discounts.objects.get(name=name_coupon, active=True)
        if coupon:
            order.discount = coupon
            order.save()
            order.calculate_total_price()
    except Discounts.DoesNotExist:
        coupon = None
        #TODO: обработка ошибки
    return redirect('/')

def add_tax(request, name_coupon):
    order = get_order(request)
    try:
        tax = Tax.objects.get(name=name_coupon, active=True)
        if tax:
            order.tax = tax
            order.save()
            order.calculate_total_price()
    except Discounts.DoesNotExist:
        tax = None
        #TODO: обработка ошибки
    return redirect('/')


#TODO: в админ панель изменить добавление предмета, убрать поля для stripe_id