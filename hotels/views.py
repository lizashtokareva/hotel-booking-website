from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from hotels.models import Booking, Hotel
from hotels.serializers import BookingSerializer, HotelSerializer

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


class HotelAPIListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20



class BookingListAPIView(APIView):

    def get(self, request, hotel_id):
        hotel = get_object_or_404(Hotel, id=hotel_id)
        bookings = Booking.objects.filter(hotel=hotel).order_by('time_start')
        serializer = BookingSerializer(bookings, many=True)

        return Response(serializer.data)

    def post(self, request, hotel_id):
        hotel = get_object_or_404(Hotel, id=hotel_id)

        serializer = BookingSerializer(
            data=request.data,
            context={'hotel': hotel}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(hotel=hotel)

        return Response(serializer.data, status=201)

class HotelAPIList(generics.ListCreateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    pagination_class = HotelAPIListPagination

class HotelAPIUpdate(generics.RetrieveUpdateAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

class HotelAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

class BookingAPIDestroy(generics.RetrieveDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

def index(request):
    # t = render_to_string('hotels/index.html')

    sort = request.GET.get("sort", "price")
    order = request.GET.get("order", "asc")

    allowed_fields = ["price", "created_at"]

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
    if request.method == "GET":
        return render(request, "hotels/index.html", context=data)
    return JsonResponse({"error": "Выбранный метод не поддерживается"}, status=405)



def about(request):
    return render(request, "hotels/about.html", {"title": "О сайте", "menu": menu})


def hotel_details(request, id):
    hotel = get_object_or_404(Hotel, id=id)

    data = {
        "title": hotel.title,
        "menu": menu,
        "content": hotel.content,
        "hotel": hotel,
    }
    if request.method == "GET":
        return render(request, "hotels/show_hotel.html", data)

    return JsonResponse({"error": "Выбран неверный метод"}, status=405)



def contact(request):
    return HttpResponse("+79121345789")


def login(request):
    return HttpResponse("Авторизация")


def page_not_found(request, exception):
    return JsonResponse({'error': 'Страница не найдена :('}, status=404)




def booking_list(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    bookings = (
        Booking.objects.filter(hotel_id=hotel_id)
        .order_by("time_start")
        .values("id", "time_start", "time_end")
    )

    if request.method == "GET":
        return render(
            request, "hotels/show_bookings.html", {"hotel": hotel, "bookings": bookings}
        )

    elif request.method == "POST":
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
            time_end__gt=time_start).exists()

        if is_booked:
            return JsonResponse({"error": "Эти даты уже заняты"}, status=409)

        booking = Booking.objects.create(
            time_start=time_start, time_end=time_end, hotel=hotel
        )

        return render(
            request, "hotels/show_bookings.html", {"hotel": hotel, "bookings": bookings})
    return JsonResponse({"error": "Выбранный метод не поддерживается"}, status=405)

def booking_details(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == "DELETE":
        booking.delete()
        return HttpResponse(status=204)

    elif request.method == "GET":
        return render(request, "hotels/show_booking.html", {"booking": booking})

    return JsonResponse({"error": "Выбранный метод не поддерживается"}, status=405)




