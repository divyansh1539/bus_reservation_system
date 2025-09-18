# reservation/migrations/0001_initial.py

from django.db import migrations, models
import django.db.models.deletion
import django.contrib.auth.models
import django.contrib.auth.validators
import django.utils.timezone
from datetime import timedelta

# UPDATED: अब यह फंक्शन भारतीय शहरों और बस नामों के साथ डेमो बसें बनाएगा
def create_demo_buses(apps, schema_editor):
    Bus = apps.get_model('reservation', 'Bus')
    
    bus_names = [
        'Rajdhani Express', 'Shatabdi Travels', 'Garuda Volvo', 
        'Shivneri Deluxe', 'Pallaki Sleeper'
    ]
    cities = [
        'Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 
        'Hyderabad', 'Pune', 'Jaipur', 'Ahmedabad', 'Lucknow'
    ]

    # पुरानी बसों को हटा दें ताकि डुप्लीकेट न बनें
    Bus.objects.all().delete()

    for i in range(50):
        source_city = cities[i % len(cities)]
        # यह सुनिश्चित करने के लिए कि स्रोत और गंतव्य अलग-अलग हों
        destination_city = cities[(i + 3) % len(cities)]
        if source_city == destination_city:
            destination_city = cities[(i + 4) % len(cities)]

        departure = django.utils.timezone.now() + timedelta(days=(i % 5), hours=(i % 24))
        
        Bus.objects.create(
            name=f'{bus_names[i % len(bus_names)]} #{i+1}',
            source=source_city,
            destination=destination_city,
            departure_time=departure,
            total_seats=40,
            available_seats=30 + (i % 10),
            ticket_price=350.00 + (i * 15) # भारतीय रुपये के हिसाब से कीमत
        )

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            # ... (CustomUser मॉडल का बाकी हिस्सा वैसा ही रहेगा) ...
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('credits', models.DecimalField(decimal_places=2, default=2000.0, max_digits=10)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={'verbose_name': 'user', 'verbose_name_plural': 'users', 'abstract': False},
            managers=[('objects', django.contrib.auth.models.UserManager())],
        ),
        # ... (Bus, Booking, और Passenger मॉडल का बाकी हिस्सा वैसा ही रहेगा) ...
        migrations.CreateModel(
            name='Bus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('source', models.CharField(max_length=100)),
                ('destination', models.CharField(max_length=100)),
                ('departure_time', models.DateTimeField()),
                ('total_seats', models.PositiveIntegerField()),
                ('available_seats', models.PositiveIntegerField()),
                ('ticket_price', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(max_length=15)),
                ('num_passengers', models.PositiveIntegerField()),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=10)),
                ('booking_time', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('Booked', 'Booked'), ('Cancelled', 'Cancelled'), ('Pending', 'Pending')], default='Pending', max_length=20)),
                ('bus', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='reservation.bus')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='reservation.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='Passenger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.PositiveIntegerField()),
                ('gender', models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=10)),
                ('booking', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='passengers', to='reservation.booking')),
            ],
        ),
        # यह फंक्शन भारतीय नामों वाली बसें बनाएगा
        migrations.RunPython(create_demo_buses),
    ]
