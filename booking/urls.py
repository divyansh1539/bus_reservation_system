"""
URL configuration for booking project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# main_app/urls.py

# booking/urls.py

# booking/urls.py

from django.contrib import admin
from django.urls import path, include
from reservation import urls

urlpatterns = [
    # 1. Admin Site URL
    # This path is for the built-in Django administration site.
    path('admin/', admin.site.urls),

    # 2. Reservation App URLs
    # This is the crucial line. It tells Django that for any URL,
    # it should look for the 'urls.py' file inside your 'reservation' app.
    path('', include('reservation.urls')),
]




