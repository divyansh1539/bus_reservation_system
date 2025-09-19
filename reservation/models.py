from django.db import models
from django.contrib.auth.models import User

class Bus(models.Model):
    name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    seats = models.IntegerField(default=40)

    def __str__(self):
        return f"{self.name} ({self.source} → {self.destination})"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE)
    seats_booked = models.IntegerField()
    booking_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="Booked")

    def __str__(self):
        return f"{self.user.username} - {self.bus.name}"


