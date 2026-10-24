from rest_framework import serializers
from .models import Hotel, Booking


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = ['id', 'title', 'content', 'price']
    price = serializers.DecimalField(
            max_digits=10,
            decimal_places=2,
            required=True
        )

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Цена должна быть больше нуля')
        return value

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'time_start', 'time_end']
        read_only_fields = ['id']

    def validate(self, attrs):
        start = attrs['time_start']
        end = attrs['time_end']

        if start >= end:
            raise serializers.ValidationError('Дата начала должна быть раньше даты окончания')

        hotel = self.context['hotel']

        is_booked = Booking.objects.filter(
            hotel=hotel,
            time_start__lt=end,
            time_end__gt=start
        ).exists()

        if is_booked:
            raise serializers.ValidationError('Эти даты уже заняты')

        return attrs