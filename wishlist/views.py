from django.shortcuts import render, redirect
from logic.services import view_in_wishlist, add_to_wishlist, remove_from_wishlist
from django.contrib.auth import get_user
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpRequest, HttpResponseNotFound


@login_required(login_url='login:login_view')
def wishlist_view(request):
    if request.method == "GET":
        current_user = get_user(request).username
        data = view_in_wishlist(request)        # wishlist = {user: {'products': []}}

        products = data[current_user]['products']

        return render(request, 'wishlist/wishlist.html', context={"products": products})


@login_required(login_url='login:login_view')
def wishlist_json(request):
    """
    Просмотр всех продуктов в избранном для пользователя и возвращение этого в JSON
    """
    if request.method == "GET":
        current_user = get_user(request).username
        data = view_in_wishlist(request)
        if data:
            return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

        return JsonResponse({"answer": 'Пользователь не авторизован.'}, status=404, json_dumps_params={'ensure_ascii': False})


@login_required(login_url='login:login_view')
def wishlist_add_json(request, id_product: str):
    if request.method == "GET":
        result = add_to_wishlist(request, id_product)
        if result:
            return JsonResponse({"answer": "Продукт успешно добавлен в избранное"},
                                json_dumps_params={'ensure_ascii': False})

        return JsonResponse({"answer": "Неудачное добавление в избранное"}, status=404, json_dumps_params={'ensure_ascii': False})


def wishlist_del_json(request, id_product: str):
    if request.method == "GET":
        result = remove_from_wishlist(request, id_product)
        if result:
            return JsonResponse({"answer": "Продукт успешно удалён из избранного"},
                                json_dumps_params={'ensure_ascii': False})

        return JsonResponse({"answer": "Неудачное удаление из избранного"},
                            status=404, json_dumps_params={'ensure_ascii': False})


def wishlist_remove_view(request, id_product):
    if request.method == "GET":
        result = remove_from_wishlist(request, id_product)  # Вызвать функцию удаления из избранного
        if result:
            return redirect("wishlist:wishlist_view")  # Вернуть перенаправление в избранное

        return HttpResponseNotFound("Неудачное удаление из избранного")
