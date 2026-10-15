from django.db import models
from django.urls import reverse
# Create your models here.

class FreeHotelManager(models.Manager):
     def get_queryset(self):
          return super().get_queryset().filter(is_free=Hotel.Status.FREE)

class Hotel(models.Model):
     class Status(models.IntegerChoices):
          DRAFT = 0, 'Занят'
          FREE = 1, 'Свободен'

     id = models.AutoField(primary_key=True)
     title = models.CharField(max_length=100)
     content = models.TextField(blank = True)
     time_create = models.DateTimeField(auto_now_add=True)
     time_update = models.DateTimeField(auto_now=True)
     is_free = models.BooleanField(choices=Status.choices, default=Status.FREE)
     slug = models.SlugField(max_length=255, unique=True, db_index=True, default=f'{id}.slug')
     price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

     objects = models.Manager()
     free = FreeHotelManager()

     def __str__(self):
          return self.title

     class Meta:
          ordering = ['-time_create']
          indexes = [models.Index(fields=['time_create'])]

     def get_absolute_url(self):
          return reverse('hotel', kwargs={'id': self.id})


class Booking(models.Model):
    time_start = models.DateField()
    time_end = models.DateField()
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE
    )

    objects = models.Manager()