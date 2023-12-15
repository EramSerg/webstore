import requests
from django.shortcuts import render
from datetime import datetime
from django.http import JsonResponse, HttpRequest, HttpResponse
from .func_api_weather import current_weather


def weather_view(request: HttpRequest):
    if request.method == "GET":
        lat = request.GET.get('lat')
        lon = request.GET.get('lon')
        if lat and lon:
            data = current_weather(lat=lat, lon=lon)
        else:
            data = current_weather()

        return JsonResponse(data, json_dumps_params={'ensure_ascii': False, 'indent': 4})

