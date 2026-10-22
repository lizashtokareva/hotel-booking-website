from datetime import date

from django.test import TestCase
from django.urls import reverse

from .models import Booking, Hotel


class BookingTests(TestCase):

    def setUp(self):
        self.hotel = Hotel.objects.create(content = 'Тестовый номер', price=3000)

    def test_nonexistent_hotel_returns_404(self):
        url=(reverse("show_bookings", kwargs={'hotel_id': 9999}))

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_create_booking(self):
        url = reverse('show_bookings', kwargs={'hotel_id': self.hotel.id})

        response = self.client.post(url, data={'time_start': '2026-10-20', 'time_end': '2026-10-25'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Booking.objects.count(), 1)

        booking = Booking.objects.get(hotel=self.hotel)
        self.assertEqual(booking.time_start, date(2026, 10, 20))
        self.assertEqual(booking.time_end, date(2026, 10, 25))

    def test_booking_overlap(self):
        url = reverse('show_bookings', kwargs={'hotel_id': self.hotel.id})
        Booking.objects.create(hotel=self.hotel, time_start='2026-10-20', time_end='2026-10-25')
        cases = [('Пересечение справа', '2026-10-23', '2026-10-26'),
                 ('Пересечение слева', '2026-10-18', '2026-10-22'),
                 ('Полное совпадение', '2026-10-20', '2026-10-25'),
                 ('Полный охват', '2026-10-18', '2026-10-28'),
                 ('Полное нахождение внутри', '2026-10-21', '2026-10-4')
                 ]


        for name, start, end in cases:
            with self.subTest(case=name):
                response = self.client.post(url, data= {'time_start': start, 'time_end': end})
                self.assertEqual(response.status_code, 400)
                self.assertEqual(Booking.objects.count(), 1)

    def test_create_wrong_date(self):
        url = reverse('show_bookings', kwargs={'hotel_id': self.hotel.id})

        response = self.client.post(url, data={'time_start': 2026-10-20, 'time_end': 2026-10-25})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Booking.objects.count(), 0)

    def test_delete_booking_returns_302(self):
        booking = Booking.objects.create(time_start='2026-10-20', time_end='2026-10-25', hotel=self.hotel)
        url = reverse('delete_booking', kwargs={'booking_id': booking.idс})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Booking.objects.count(), 0)

class HotelTests(TestCase):

    def test_wrong_price(self):
        url = reverse('add_hotel')
        cases = [('Отрицательная цена', -500),
                 ('Цена не является числом', 'тысяча'),
                 ]

        for name, price in cases:
            with self.subTest(case=name):
                response = self.client.post(url, data={'title': 'Тестовый отель', 'price': price})
                self.assertEqual(response.status_code, 400)
                self.assertEqual(Hotel.objects.count(), 0)

    def test_empty_title(self):
        url = reverse('add_hotel')

        response = self.client.post(url, data={'title': '', 'price': 3000})
        self.assertEqual(response.status_code, 400)

    def test_nonexistent_hotel_returns_404(self):
        url=(reverse("hotel", kwargs={'id': 9999}))

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_delete_hotel(self):
        hotel = Hotel.objects.create(content = 'Тестовый отель', price=3000)
        url = reverse('delete_hotel', kwargs={'id': hotel.id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Hotel.objects.count(), 0)





