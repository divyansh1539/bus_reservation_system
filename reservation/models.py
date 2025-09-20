# reservation/models.py

import random
from django.db import models
from django.contrib.auth.models import AbstractUser

# --- टिकट ID बनाने वाले फंक्शन्स ---
def generate_booking_ticket_id():
    """ 6-अंकों का एक यूनिक बुकिंग ID जेनरेट करता है """
    return str(random.randint(100000, 999999))

def generate_passenger_ticket_id():
    """ 8-अंकों का एक यूनिक पैसेंजर टिकट ID जेनरेट करता है """
    return str(random.randint(10000000, 99999999))

class CustomUser(AbstractUser):
    credits = models.DecimalField(max_digits=10, decimal_places=2, default=2000.00)

class Bus(models.Model):
    name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    total_seats = models.PositiveIntegerField()
    available_seats = models.PositiveIntegerField()
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.source} to {self.destination})"

class Booking(models.Model):
    ticket_id = models.CharField(max_length=6, unique=True, blank=True, editable=False)
    journey_date = models.DateField(null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='bookings')
    phone_number = models.CharField(max_length=15)
    num_passengers = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    booking_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Booked', 'Booked'), ('Cancelled', 'Cancelled'), ('Pending', 'Pending')], default='Pending')

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            while True:
                new_id = generate_booking_ticket_id()
                if not Booking.objects.filter(ticket_id=new_id).exists():
                    self.ticket_id = new_id
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.ticket_id} by {self.user.username}"

class Passenger(models.Model):
    # --- बदलाव यहाँ है: हमने null=True, blank=True जोड़ा है ---
    seat_number = models.CharField(max_length=10, null=True, blank=True)

    ticket_id = models.CharField(max_length=8, unique=True, blank=True, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='passengers')
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    def save(self, *args, **kwargs):
        if not self.ticket_id:
            while True:
                new_id = generate_passenger_ticket_id()
                if not Passenger.objects.filter(ticket_id=new_id).exists():
                    self.ticket_id = new_id
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Passenger {self.name} ({self.ticket_id}) for Booking {self.booking.ticket_id}"


 
