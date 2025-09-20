# reservation/views.py

import io
from datetime import timedelta

from django.utils import timezone
from django.http import FileResponse
from django.core.mail import EmailMessage
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.forms import formset_factory

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

from .models import Bus, Booking, Passenger
from .forms import CustomUserCreationForm, BusSearchForm, PassengerFormSet, BookingDetailsForm


def generate_ticket_pdf(booking, passengers):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=40)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("Bus Reservation Ticket", styles['h1']))
    elements.append(Spacer(1, 24))
    try:
        journey_date_str = booking.journey_date.strftime('%b %d, %Y')
    except AttributeError:
        journey_date_str = booking.bus.departure_time.strftime('%b %d, %Y')
    booking_info = [
        ["Booking ID:", booking.ticket_id],
        ["Bus:", booking.bus.name],
        ["Route:", f"{booking.bus.source} to {booking.bus.destination}"],
        ["Journey Date:", journey_date_str],
        ["Departure:", booking.bus.departure_time.strftime('%I:%M %p')],
    ]
    booking_table = Table(booking_info, colWidths=[120, 380])
    booking_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#3c2a0b")),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#a389a1")),
        ('TEXTCOLOR', (0,0), (0,-1), colors.white),
    ]))
    elements.append(booking_table)
    elements.append(Spacer(1, 24))
    elements.append(Paragraph("Passenger Details", styles['h2']))
    passenger_data = [["Ticket ID", "Name", "Age", "Gender", "Seat"]]
    for p in passengers:
        passenger_data.append([p.ticket_id, p.name, str(p.age), p.gender, p.seat_number])
    passenger_table = Table(passenger_data, colWidths=[100, 180, 50, 80, 70])
    passenger_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#026a47")), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elements.append(passenger_table)
    doc.build(elements)
    buffer.seek(0)
    return buffer


@login_required
def confirm_payment_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user, status='Pending')

    if request.method == 'POST':
        if request.user.credits >= booking.total_cost:
           
            request.user.credits -= booking.total_cost
            request.user.save()
            booking.bus.available_seats -= booking.num_passengers
            booking.bus.save()
            booking.status = 'Booked'
            booking.save()

            messages.success(request, f"Booking successful! {booking.total_cost} credits deducted.")

            
            try:
                passengers = booking.passengers.all()
                
                pdf_buffer = generate_ticket_pdf(booking, passengers)

                
                subject = f"Your Ticket is Confirmed: Booking ID BOOK-{booking.id}"
                body = (
                    f"Dear {booking.user.username},\n\n"
                    f"Your booking for {booking.bus.name} is confirmed. Please find your ticket attached.\n\n"
                    "Thank you for using our service!"
                )
                email = EmailMessage(
                    subject,
                    body,
                    'your_gmail_address@gmail.com', 
                    [booking.user.email]
                )
                
                
                email.attach(f'Ticket-BOOK-{booking.id}.pdf', pdf_buffer.getvalue(), 'application/pdf')
                email.send(fail_silently=False)
                
                messages.info(request, 'A confirmation email with your ticket has been sent.')
            except Exception as e:
                
                messages.error(request, f"Booking was successful, but failed to send email: {e}")
           
            return redirect('index')
        else:
            messages.error(request, "You do not have enough credits.")
            return redirect('confirm_payment', booking_id=booking.id)

    return render(request, 'payment.html', {'booking': booking})




def register_view(request):
    if request.user.is_authenticated: return redirect('index')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid(): form.save(); messages.success(request, 'Account created!'); return redirect('login')
    else: form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated: return redirect('index')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            if user is not None: login(request, user); return redirect('index')
    else: form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request); return redirect('login')

# ---- APP CORE VIEWS ----
@login_required
def index_view(request):
    now = timezone.now()
    end_date = now + timedelta(days=7)
    buses = Bus.objects.filter(departure_time__range=[now, end_date], available_seats__gt=0).order_by('departure_time')
    user_bookings = request.user.bookings.all().order_by('-booking_time')
    return render(request, 'index.html', {'buses': buses, 'bookings': user_bookings})

@login_required
def book_ticket_view(request):
    if request.method == 'POST':
        form = BusSearchForm(request.POST)
        if form.is_valid():
            buses = Bus.objects.filter(source__iexact=form.cleaned_data['source'], destination__iexact=form.cleaned_data['destination'], departure_time__date=form.cleaned_data['journey_date'], available_seats__gt=0)
            return render(request, 'bus_list.html', {'buses': buses, 'journey_date': form.cleaned_data['journey_date']})
    else: form = BusSearchForm()
    return render(request, 'book_ticket.html', {'search_form': form})

@login_required
def book_bus_view(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    booked_seats = Passenger.objects.filter(booking__bus=bus, booking__status='Booked').values_list('seat_number', flat=True)
    all_seats = [str(i) for i in range(1, bus.total_seats + 1)]
    available_seats = [seat for seat in all_seats if seat not in booked_seats]
    PassengerFormSet = formset_factory(PassengerForm, extra=1)
    details_form = BookingDetailsForm(request.POST or None)
    passenger_formset = PassengerFormSet(request.POST or None, prefix='form', form_kwargs={'available_seats': available_seats})
    if request.method == 'POST':
        if details_form.is_valid() and passenger_formset.is_valid():
            chosen_seats = [form_data.get('seat_number') for form_data in passenger_formset.cleaned_data if form_data]
            if len(chosen_seats) != len(set(chosen_seats)):
                messages.error(request, "Each passenger must have a unique seat.")
                return render(request, 'enter_passengers.html', {'bus': bus, 'details_form': details_form, 'passenger_formset': passenger_formset})
            num_passengers = len(chosen_seats)
            if len(available_seats) < num_passengers:
                messages.error(request, f"Sorry, only {len(available_seats)} seats are available.")
                return redirect('book_bus', bus_id=bus.id)
            booking = details_form.save(commit=False)
            booking.user = request.user; booking.bus = bus; booking.num_passengers = num_passengers
            booking.total_cost = bus.ticket_price * num_passengers; booking.status = 'Pending'
            booking.journey_date = bus.departure_time.date()
            booking.save()
            for form_data in passenger_formset.cleaned_data:
                if form_data:
                    Passenger.objects.create(booking=booking, name=form_data.get('name'), age=form_data.get('age'), gender=form_data.get('gender'), seat_number=form_data.get('seat_number'))
            messages.success(request, "Details saved. Please proceed to payment.")
            return redirect('confirm_payment', booking_id=booking.id)
    context = {'bus': bus, 'details_form': details_form, 'passenger_formset': passenger_formset}
    return render(request, 'enter_passengers.html', context)

@login_required
def confirm_payment_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user, status='Pending')
    if request.method == 'POST':
        if request.user.credits >= booking.total_cost:
            request.user.credits -= booking.total_cost; request.user.save()
            booking.bus.available_seats -= booking.num_passengers; booking.bus.save()
            booking.status = 'Booked'; booking.save()
            send_booking_confirmation_email(booking)
            messages.success(request, "Booking successful! A confirmation email has been sent.")
            return redirect('index')
        else: messages.error(request, "You do not have enough credits."); return redirect('confirm_payment', booking_id=booking.id)
    return render(request, 'payment.html', {'booking': booking})

@login_required
def cancel_booking_view(request, booking_id):
    try: booking = Booking.objects.get(id=booking_id, user=request.user, status='Booked')
    except Booking.DoesNotExist:
        messages.error(request, "This booking does not exist or has already been cancelled.")
        return redirect('index')
    if request.method == 'POST':
        request.user.credits += booking.total_cost; request.user.save()
        booking.bus.available_seats += booking.num_passengers; booking.bus.save()
        booking.status = 'Cancelled'; booking.save()
        send_cancellation_email(booking)
        messages.success(request, "Booking has been successfully cancelled and credits have been refunded.")
        return redirect('index')
    return render(request, 'cancel_booking_confirm.html', {'booking': booking})

@login_required
def booking_detail_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    passengers = booking.passengers.all()
    return render(request, 'booking_detail.html', {'booking': booking, 'passengers': passengers})

@login_required
def download_ticket_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    passengers = booking.passengers.all()
    pdf_buffer = generate_ticket_pdf(booking, passengers)
    return FileResponse(pdf_buffer, as_attachment=True, filename=f'Ticket-{booking.ticket_id}.pdf')
