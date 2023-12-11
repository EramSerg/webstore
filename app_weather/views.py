import requests
from django.shortcuts import render
from datetime import datetime
from django.http import JsonResponse, HttpRequest, HttpResponse
from .func_api_weather import current_weather


def weather_view(request: HttpRequest):
    if request.method == "GET":
        return current_weather()

