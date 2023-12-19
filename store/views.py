from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpRequest, HttpResponseNotFound
from .models import DATABASE
from logic.services import filtering_category, view_in_cart, add_to_cart, remove_from_cart


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
                data = filtering_category(DATABASE, category_key, ordering_key, reverse=True) #  TODO Провести фильтрацию с параметрами
            else:
                data = filtering_category(DATABASE, category_key, ordering_key) #  TODO Провести фильтрацию с параметрами
        else:
            data = filtering_category(DATABASE, category_key) #  TODO Провести фильтрацию с параметрами
        # В этот раз добавляем параметр safe=False, для корректного отображения списка в JSON
        return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False, 'indent': 4})


def shop_view(request: HttpRequest):
    if request.method == "GET":
        return render(request, 'store/shop.html', context={"products": DATABASE.values()})


def products_page_view(request, page):
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

        return HttpResponse(status=404)


def cart_view(request):
    if request.method == "GET":
        data = view_in_cart()
        if request.GET.get('format') == 'JSON':
            return JsonResponse(data, json_dumps_params={'ensure_ascii': False, 'indent': 4})

        products = []
        for product_id, quantity in data['products'].items():
            product = DATABASE[product_id]
            cart = view_in_cart()
            quantity = cart['products'][product_id]
            product.update({'quantity': quantity})
            products.append(product)

        return render(request, 'store/cart.html', context={'products': products})


def cart_add_view(request, id_product):
    if request.method == "GET":
        result = add_to_cart(id_product) # TODO Вызвать ответственную за это действие функцию
        if result:
            return JsonResponse({"answer": "Продукт успешно добавлен в корзину"},
                                json_dumps_params={'ensure_ascii': False})

        return JsonResponse({"answer": "Неудачное добавление в корзину"},
                            status=404, json_dumps_params={'ensure_ascii': False})


def cart_del_view(request, id_product):
    if request.method == "GET":
        result = remove_from_cart(id_product)  # TODO Вызвать ответственную за это действие функцию
        if result:
            return JsonResponse({"answer": "Продукт успешно удалён из корзины"},
                                json_dumps_params={'ensure_ascii': False})

        return JsonResponse({"answer": "Неудачное удаление из корзины"},
                            status=404, json_dumps_params={'ensure_ascii': False})


