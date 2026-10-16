from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from hotels.models import Booking, Hotel

menu = [
    {"title": "О сайте", "url_name": "about"},
    {"title": "Выбрать отель", "url_name": "home"},
    {"title": "Обратная связь", "url_name": "contact"},
    {"title": "Войти", "url_name": "login"},
]

data_db = [
    {"id": 1, "title": "Hyatt", "content": "Пятизвёздочный отель", "is_free": True},
    {
        "id": 2,
        "title": "Radisson",
        "content": "Четырёхзвёздочный отель",
        "is_free": False,
    },
    {"id": 3, "title": "Azimut", "content": "Четырёхзвёздочный отель", "is_free": True},
]


def index(request):
    # t = render_to_string('hotels/index.html')

    sort = request.GET.get("sort", "price")
    order = request.GET.get("order", "asc")

    allowed_fields = ["price", "time_create"]

    if sort not in allowed_fields:
        return JsonResponse(
            {"error": "Сортировка допускается только по времени создания и по цене"},
            status=400,
        )

    if order == "desc":
        sort = "-" + sort

    if order not in ["asc", "desc"]:
        return JsonResponse(
            {"error": "Недопустимое направление сортировки"}, status=400
        )

    hotel = Hotel.free.order_by(sort)
    data = {
        "title": "главная страница",
        "menu": menu,
        "hotel": hotel,
    }

    return render(request, "hotels/index.html", context=data)


def about(request):
    return render(request, "hotels/about.html", {"title": "О сайте", "menu": menu})


def show_hotel(request, id):
    hotel = get_object_or_404(Hotel, id=id)

    data = {
        "title": hotel.title,
        "menu": menu,
        "content": hotel.content,
        "hotel": hotel,
    }

    return render(request, "hotels/show_hotel.html", data)


def contact(request):
    return HttpResponse("+79121345789")


def login(request):
    return HttpResponse("Авторизация")


def page_not_found(request, exception):
    return JsonResponse({'error': 'Страница не найдена :('}, status=404)


def add_hotel(request):
    if request.method == "POST":
        description = request.POST.get("content")
        title = request.POST.get("title")
        try:
            price = Decimal(request.POST.get("price", ""))

        except (ValueError, TypeError, InvalidOperation):
            return JsonResponse({"error": "Цена должна быть числом"}, status=400)

        if price <= 0:
            return JsonResponse({"error": "<Цена должна быть больше нуля"}, status=400)

        if not title:
            return JsonResponse({"error": "Название не может быть пустым"}, status=400)

        new_obj = Hotel.objects.create(title=title, content=description, price=price)

        return redirect("home")

    if request.method == "GET":
        return render(request, "hotels/add_hotel.html")

    return JsonResponse({"error": "Неверный метод"}, status=405)


def delete_hotel(request, id):
    if request.method == "POST":
        hotel = get_object_or_404(Hotel, id=id)
        hotel.delete()
        return redirect("home")

    return JsonResponse({"error": "Метод не поддерживается"}, status=405)


def show_bookings(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    bookings = (
        Booking.objects.filter(hotel_id=hotel_id)
        .order_by("time_start")
        .values("id", "time_start", "time_end")
    )

    if request.method == "POST":
        raw_start = request.POST.get("time_start")
        raw_end = request.POST.get("time_end")

        try:
            time_start = datetime.strptime(raw_start, "%Y-%m-%d").date()

            time_end = datetime.strptime(raw_end, "%Y-%m-%d").date()

        except (ValueError, TypeError):
            return JsonResponse({"error": "Некорректная дата"}, status=400)

        if time_start >= time_end:
            return JsonResponse({"error": "Некорректные даты"}, status=400)

        if raw_start != time_start.isoformat() or raw_end != time_end.isoformat():
            return JsonResponse({"error": "Некорректный формат даты"}, status=400)


        is_booked = Booking.objects.filter(
            hotel=hotel,
            time_start__lt=time_end,
            time_end__gt=time_start)

        if is_booked:
            return JsonResponse({"error": "Эти даты уже заняты"}, status=400)

        booking = Booking.objects.create(
            time_start=time_start, time_end=time_end, hotel=hotel
        )

        return render(
            request, "hotels/show_bookings.html", {"hotel": hotel, "bookings": bookings}
        )

    if request.method == "GET":
        return render(
            request, "hotels/show_bookings.html", {"hotel": hotel, "bookings": bookings}
        )

    return JsonResponse({"error": "Выбран неверный метод"}, status=405)


def delete_booking(request, booking_id):
    if request.method == "POST":
        booking = get_object_or_404(Booking, id=booking_id)
        booking.delete()
        hotel_id = booking.hotel_id
        return redirect("show_bookings", hotel_id=hotel_id)

    return JsonResponse({"error": "Выбран неверный метод"}, status=405)
