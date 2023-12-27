from django.contrib.auth import get_user
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpRequest, HttpResponseNotFound
from .models import DATABASE
from logic.services import filtering_category, view_in_cart, add_to_cart, remove_from_cart
from django.contrib.auth.decorators import login_required


def products_view(request):
    if request.method == "GET":
        # Обработка id из параметров запроса (уже было реализовано ранее)
        if id_product := request.GET.get("id"):
            if data := DATABASE.get(id_product):
                return JsonResponse(data, json_dumps_params={'ensure_ascii': False,
                                                             'indent': 4})
            return HttpResponseNotFound("Данного продукта нет в базе данных")

        # Обработка фильтрации из параметров запроса
        category_key = request.GET.get("category")  # Считали 'category'
        if ordering_key := request.GET.get("ordering"): # Если в параметрах есть 'ordering'
            if request.GET.get("reverse") in ('true', 'True'): # Если в параметрах есть 'ordering' и 'reverse'=True
                data = filtering_category(DATABASE, category_key, ordering_key, reverse=True) #  Провести фильтрацию с параметрами
            else:
                data = filtering_category(DATABASE, category_key, ordering_key) #  Провести фильтрацию с параметрами
        else:
            data = filtering_category(DATABASE, category_key) #  Провести фильтрацию с параметрами
        # В этот раз добавляем параметр safe=False, для корректного отображения списка в JSON
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4})


def shop_view(request: HttpRequest):
    if request.method == "GET":
        category_key = request.GET.get("category")
        if ordering_key := request.GET.get("ordering"):
            if request.GET.get("reverse") in ('true', 'True'):
                data = filtering_category(DATABASE, category_key, ordering_key, True)
            else:
                data = filtering_category(DATABASE, category_key, ordering_key)
        else:
            data = filtering_category(DATABASE, category_key)
        return render(request, 'store/shop.html', context={"products": data, "category": category_key})


'''def products_page_view(request, page):
    if request.method == "GET":
        if isinstance(page, str):
            for data in DATABASE.values():
                if data['html'] == page:  # Если значение переданного параметра совпадает именем html файла
                    with open(f'store/products/{page}.html', encoding='utf-8') as page:
                        data = page.read()
                    return HttpResponse(data)
        elif isinstance(page, int):
            data = DATABASE.get(str(page))
            if data:
                with open(f"store/products/{data['html']}.html", encoding='utf-8') as page:
                    res = page.read()
                return HttpResponse(res)

        return HttpResponse(status=404)'''


def products_page_view(request, page):
    if request.method == "GET":
        if isinstance(page, str):
            for data in DATABASE.values():
                if data['html'] == page:
                    return render(request, "store/product.html", context={"product": data})

        elif isinstance(page, int):
            # Обрабатываем условие того, что пытаемся получить страницу товара по его id
            data = DATABASE.get(str(page))  # Получаем какой странице соответствует данный id
            if data:
                return render(request, "store/product.html", context={"product": data})

        return HttpResponse(status=404)


@login_required(login_url='login:login_view')
def cart_view(request):
    if request.method == "GET":
        current_user = get_user(request).username
        data = view_in_cart(request)[current_user]
        if request.GET.get('format') == 'JSON':
            return JsonResponse(data, json_dumps_params={'ensure_ascii': False, 'indent': 4})

        products = []
        for product_id, quantity in data['products'].items():
            product = DATABASE[product_id]
            product['quantity'] = quantity
            product['price_total'] = f'{quantity * product["price_after"]:.2f}'
            products.append(product)

        return render(request, 'store/cart.html', context={'products': products})


@login_required(login_url='login:login_view')
def cart_add_view(request, id_product):
    if request.method == "GET":
        result = add_to_cart(request, id_product)
        if result:
            return JsonResponse({"answer": "Продукт успешно добавлен в корзину"},
                                json_dumps_params={'ensure_ascii': False})

        return JsonResponse({"answer": "Неудачное добавление в корзину"},
                            status=404, json_dumps_params={'ensure_ascii': False})


def cart_del_view(request, id_product):
    if request.method == "GET":
        result = remove_from_cart(request, id_product)
        if result:
            return JsonResponse({"answer": "Продукт успешно удалён из корзины"},
                                json_dumps_params={'ensure_ascii': False})

        return JsonResponse({"answer": "Неудачное удаление из корзины"},
                            status=404, json_dumps_params={'ensure_ascii': False})


def coupon_check_view(request, name_coupon):

    DATA_COUPON = {
        "coupon": {
            "value": 10,
            "is_valid": True},
        "coupon_old": {
            "value": 20,
            "is_valid": False},
    }

    if request.method == "GET":
        if name_coupon in DATA_COUPON:
            data = {"discount": DATA_COUPON[name_coupon]["value"], "is_valid": DATA_COUPON[name_coupon]["is_valid"]}
            return JsonResponse(data, json_dumps_params={'ensure_ascii': False})

    return HttpResponseNotFound("Неверный купон")


def delivery_estimate_view(request):
    DATA_PRICE = {
        "Россия": {
            "Москва": {"price": 80},
            "Санкт-Петербург": {"price": 80},
            "fix_price": 100,
        },
    }
    if request.method == "GET":
        data = request.GET
        country = data.get('country')
        city = data.get('city')
        if city in DATA_PRICE[country]:
            return JsonResponse(DATA_PRICE[country][city], json_dumps_params={'ensure_ascii': False})
        elif city not in DATA_PRICE[country]:
            return JsonResponse({"price": DATA_PRICE[country]["fix_price"]}, json_dumps_params={'ensure_ascii': False})

    return HttpResponseNotFound("Неверные данные")


@login_required(login_url='login:login_view')
def cart_buy_now_view(request, id_product):
    if request.method == "GET":
        result = add_to_cart(request, id_product)
        if result:
            return redirect("store:cart_view")

        return HttpResponseNotFound("Неудачное добавление в корзину")


def cart_remove_view(request, id_product):
    if request.method == "GET":
        result = remove_from_cart(request, id_product)  # Вызвать функцию удаления из корзины
        if result:
            return redirect("store:cart_view")  # Вернуть перенаправление на корзину

        return HttpResponseNotFound("Неудачное удаление из корзины")