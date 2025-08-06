from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import TemplateView

def home_page(request):
    return render(request, 'payment/home.html')

def cat(request):
    return HttpResponse("Meow.")