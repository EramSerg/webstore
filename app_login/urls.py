from django.urls import path
from app_login.views import login_view, logout_view

app_name = 'login'

urlpatterns = [
    path('', login_view, name="login_view"),
    path('/login', logout_view, name="logout_view"),
]