# reservation/views.py

# --- शुरुआत में ये नए imports जोड़ें ---
import io
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
from .models import Bus, Booking, Passenger
from .forms import CustomUserCreationForm, BusSearchForm, PassengerFormSet, BookingDetailsForm


def generate_ticket_pdf(booking, passengers):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("Bus Reservation Ticket", styles['h1']))
    elements.append(Spacer(1, 24))

    # Booking Info
    booking_info = [
        ["Booking ID:", f"BOOK-{booking.id}"],
        ["Bus:", booking.bus.name],
        ["Route:", f"{booking.bus.source} to {booking.bus.destination}"],
        ["Departure:", booking.bus.departure_time.strftime('%b %d, %Y, %I:%M %p')],
    ]
    booking_table = Table(booking_info, colWidths=[120, 380])
    booking_table.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'), ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#3c2a0b")),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#a389a1")), ('TEXTCOLOR', (0,0), (0,-1), colors.white),
    ]))
    elements.append(booking_table)
    elements.append(Spacer(1, 24))

    # Passenger Info
    elements.append(Paragraph("Passenger Details", styles['h2']))
    passenger_data = [["Ticket ID", "Name", "Age", "Gender"]]
    for p in passengers:
        passenger_data.append([f"TICKET-{booking.id}-{p.id}", p.name, str(p.age), p.gender])
    
    passenger_table = Table(passenger_data, colWidths=[120, 200, 60, 120])
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
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else: form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated: return redirect('index')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data.get('username'), password=form.cleaned_data.get('password'))
            if user is not None:
                login(request, user)
                return redirect('index')
    else: form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request); return redirect('login')

@login_required
def index_view(request):
    buses = Bus.objects.filter(available_seats__gt=0).order_by('departure_time')
    user_bookings = request.user.bookings.filter(status='Booked').order_by('-booking_time')
    context = {'buses': buses, 'bookings': user_bookings}
    return render(request, 'index.html', context)

@login_required
def book_ticket_view(request):
    if request.method == 'POST':
        form = BusSearchForm(request.POST)
        if form.is_valid():
            buses = Bus.objects.filter(source__iexact=form.cleaned_data['source'], destination__iexact=form.cleaned_data['destination'], available_seats__gt=0)
            return render(request, 'bus_list.html', {'buses': buses})
    else: form = BusSearchForm()
    return render(request, 'book_ticket.html', {'search_form': form})

@login_required
def book_bus_view(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)
    details_form = BookingDetailsForm(request.POST or None)
    passenger_formset = PassengerFormSet(request.POST or None, prefix='form')
    if request.method == 'POST':
        if details_form.is_valid() and passenger_formset.is_valid():
            num_passengers = len(passenger_formset.cleaned_data)
            if bus.available_seats < num_passengers:
                messages.error(request, f"Sorry, only {bus.available_seats} seats are available.")
                return redirect('book_bus', bus_id=bus.id)
            booking = details_form.save(commit=False)
            booking.user = request.user; booking.bus = bus; booking.num_passengers = num_passengers
            booking.total_cost = bus.ticket_price * num_passengers; booking.status = 'Pending'
            booking.save()
            for form_data in passenger_formset.cleaned_data:
                if form_data: Passenger.objects.create(booking=booking, **form_data)
            messages.success(request, "Details saved. Please proceed to payment.")
            return redirect('confirm_payment', booking_id=booking.id)
        else: messages.error(request, "Please correct the errors below.")
    context = {'bus': bus, 'details_form': details_form, 'passenger_formset': passenger_formset}
    return render(request, 'enter_passengers.html', context)

@login_required
def cancel_booking_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user, status='Booked')
    if request.method == 'POST':
        request.user.credits += booking.total_cost; request.user.save()
        booking.bus.available_seats += booking.num_passengers; booking.bus.save()
        booking.delete()
        messages.success(request, f"Booking cancelled and {booking.total_cost} credits refunded.")
        return redirect('index')
    return render(request, 'cancel_booking_confirm.html', {'booking': booking})

@login_required
def booking_detail_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    passengers = booking.passengers.all()
    context = {'booking': booking, 'passengers': passengers}
    return render(request, 'booking_detail.html', context)

@login_required
def download_ticket_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    passengers = booking.passengers.all()
    pdf_buffer = generate_ticket_pdf(booking, passengers)
    return FileResponse(pdf_buffer, as_attachment=True, filename=f'Ticket-BOOK-{booking.id}.pdf')

