from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.urls import reverse
import uuid
import string
import random
from datetime import datetime


# Create your models here.
#User._meta.get_field('email')._unique = True


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class Vehicle(models.Model):
    vehicle_type = models.CharField(max_length=256, verbose_name="Vehicle Type", choices=[("Sedan", "Sedan"), ("SUV", "SUV"), ("Coupe", "Coupe"), ("Convertible", "Convertible")], default="Sedan")
    vehicle_make = models.CharField(max_length=256, default="", verbose_name="Make")
    plate_number = models.CharField(max_length=256, default="", verbose_name="Plate Number")
    vehicle_capacity = models.IntegerField(default=4, verbose_name="Capacity")
    special_vehicle_info = models.TextField(default="", verbose_name="Special Vehicle Info")



class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name='driver', blank=True, null=True)
    license_no = models.CharField(max_length=256, verbose_name="License Number")
    driver_status = models.CharField(max_length=256, default="No")
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, related_name="driver", blank=True, null=True)



class Sharer(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sharer', blank = True, null = True)
    dest_arr = models.CharField(max_length=256, default="")
    earliest_time = models.DateTimeField(default = datetime.now().strftime('%Y-%m-%d %H:%M'), verbose_name='Earliest Time')
    latest_time = models.DateTimeField(default = datetime.now().strftime('%Y-%m-%d %H:%M'), verbose_name='Latest Time')
    no_persons_sharer = models.PositiveIntegerField(verbose_name='Number of Passengers', default=1, validators=[MinValueValidator(1)])



class Ride(models.Model):
    #owner_name = models.CharField(max_length=256, default='')
    #owner_email = models.EmailField(max_length = 256)
    #sharer_email = models.EmailField(max_length = 256, default='@', blank = True

    # owner info
    unique_id = models.CharField(max_length=6, null=True, blank=True, unique=True)
    owner = models.ForeignKey(User, on_delete = models.PROTECT, related_name="owner", default=2)
    dest_addr = models.CharField(max_length=512, verbose_name='Your Destination', default = "")
    arr_date_time = models.DateTimeField(default = datetime.now().strftime('%Y-%m-%d %H:%M'), verbose_name='Arrival Time')
    no_persons_owner = models.PositiveIntegerField(verbose_name='Number of Passengers', default = 1, validators=[MinValueValidator(1)])
    owner_vehicle_type = models.CharField(max_length=256, verbose_name="Vehicle Type", choices=[("All", "All"), ("Sedan", "Sedan"), ("SUV", "SUV"), ("Coupe", "Coupe"), ("Convertible", "Convertible")], default="All")
    special_request = models.TextField(verbose_name='Special Request', blank = True)
    can_shared = models.BooleanField(verbose_name='Share your ride', default = False)
    max_allowed_persons = models.IntegerField(verbose_name="Max Sharers Allowed", validators=[MinValueValidator(1)], blank=True, null=True)

    # sharer info

    # driver info
    sharer = models.ManyToManyField(Sharer, related_name='sharer', )
    driver = models.ForeignKey(Driver, on_delete=models.PROTECT, related_name="rides", blank=True, null=True)
    status = models.CharField(max_length = 256, default="", )


    def save(self):
        if not self.unique_id:
            self.unique_id = id_generator()
            while Ride.objects.filter(unique_id=self.unique_id).exists():
                self.unique_id = id_generator()
        super(Ride, self).save()

    def get_absolute_url(self):
        return reverse('active-rides')