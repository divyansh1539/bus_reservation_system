from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Booking

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

BUS_CHOICES = [
    ('delhi-mumbai', 'Delhi → Mumbai'),
    ('bangalore-chennai', 'Bangalore → Chennai'),
    ('kolkata-patna', 'Kolkata → Patna'),
    ('pune-goa', 'Pune → Goa'),
    ('lucknow-kanpur', 'Lucknow → Kanpur'),
]

class BookingForm(forms.Form):
    bus = forms.ChoiceField(choices=BUS_CHOICES, label="Select Bus")
    passenger_name = forms.CharField(max_length=100, label="Passenger Name")
    seats = forms.IntegerField(min_value=1, max_value=10, label="Number of Seats")