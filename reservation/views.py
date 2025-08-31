from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, BookingForm
from .models import Bus, Booking

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})

def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("index")
    return render(request, "login.html")

def user_logout(request):
    logout(request)
    return redirect("login")

@login_required
def index(request):
    buses = Bus.objects.all()
    bookings = Booking.objects.filter(user=request.user)
    return render(request, "index.html", {"buses": buses, "bookings": bookings})

@login_required
def book_ticket(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            return redirect('index')
    else:
        form = BookingForm()
    return render(request, 'book_ticket.html', {'form': form})
@login_required
def cancel_ticket(request, booking_id):
    booking = Booking.objects.get(id=booking_id, user=request.user)
    booking.status = "Cancelled"
    booking.save()
    return redirect("index")

