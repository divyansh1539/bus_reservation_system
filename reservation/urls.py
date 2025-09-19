# reservation/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # --- Authentication URLs ---
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # --- Main Application URLs ---
    path('', views.index_view, name='index'), 
    path('book-ticket/', views.book_ticket_view, name='book_ticket'),
    path('book/<int:bus_id>/', views.book_bus_view, name='book_bus'),
    path('confirm-payment/<int:booking_id>/', views.confirm_payment_view, name='confirm_payment'),

    # --- Booking and Ticket URLs ---
    path('booking/<int:booking_id>/', views.booking_detail_view, name='booking_detail'),
    path('booking/cancel/<int:booking_id>/', views.cancel_booking_view, name='cancel_booking'),
    
    # --- NEW URL for downloading the ticket ---
    path('booking/download/<int:booking_id>/', views.download_ticket_view, name='download_ticket'),
]
