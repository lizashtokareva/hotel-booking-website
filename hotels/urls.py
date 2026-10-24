from django.contrib import admin
from django.urls import path, register_converter, include

from . import converters, views
from .views import HotelAPIList

register_converter(converters.FourDigitYearConverter, "year4")

urlpatterns = [
    path("", views.index, name="home"),
    path("hotel/<int:id>/", views.hotel_details, name="hotel_details"),
    path("contact/", views.contact, name="contact"),
    path("login/", views.login, name="login"),
    path("about/", views.about, name="about"),
    path("bookings/<int:booking_id>/", views.booking_details, name="booking_details"),

    path('api/v1/hotellist/', HotelAPIList.as_view()),
    path("hotel/api/<int:hotel_id>/bookings/", views.BookingListAPIView.as_view(), name="booking_list"),

]

admin.site.site_header = "Панель администрации"
admin.site.index_title = "Отели"
