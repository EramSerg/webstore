from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpRequest
from .models import DATABASE


def products_view(request: HttpRequest):
    if request.method == "GET":
        return JsonResponse(DATABASE, json_dumps_params={'ensure_ascii': False, 'indent': 4})


def shop_view(request: HttpRequest):
    if request.method == "GET":
        with open('store/shop.html', encoding="utf-8") as f:
            data = f.read()
        return HttpResponse(data)

