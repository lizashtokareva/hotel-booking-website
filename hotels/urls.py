from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, re_path, register_converter

from hotelbooking import settings
from . import views
from . import converters

register_converter(converters.FourDigitYearConverter, 'year4')

urlpatterns = [
    path('', views.index, name = 'home'),
    path('hotel/<int:id>/', views.show_hotel, name = 'hotel'),
    path('contact/', views.contact, name = 'contact'),
    path('login/', views.login, name='login'),
    path('about/', views.about, name = 'about'),
    path('add_hotel/', views.add_hotel, name = 'add_hotel'),
    path('delete_hotel/<int:id>', views.delete_hotel, name = 'delete_hotel'),
    path('hotel/<int:hotel_id>/bookings/', views.show_bookings, name='show_bookings'),
    path('bookings/<int:booking_id>/delete/', views.delete_booking, name='delete_booking'),
    #path('edit_hotel/', views.edit_hotel, name = 'edit_hotel')
    ]

admin.site.site_header = 'Панель администрации'
admin.site.index_title = 'Отели'