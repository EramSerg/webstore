from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from datetime import datetime


def datetime_view(request: HttpRequest):
    if request.method == "GET":
        now = datetime.now()
        return HttpResponse(now)
