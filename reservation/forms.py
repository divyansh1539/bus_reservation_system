# reservation/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import formset_factory
from .models import CustomUser, Passenger, Booking



class CustomUserCreationForm(UserCreationForm):
   
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email address'}))
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password2' in self.fields: del self.fields['password2']
        for field_name in self.fields: self.fields[field_name].help_text = None
        self.fields['username'].widget.attrs.update({'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password1'].label = "Password"


# BusSearchForm को journey_date फील्ड के साथ अपडेट किया गया है
class BusSearchForm(forms.Form):
    
    source = forms.CharField(label="From", required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter source city'}))
    destination = forms.CharField(label="To", required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter destination city'}))


class BookingDetailsForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['phone_number']
        widgets = {
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter contact number'}),
        }


class PassengerForm(forms.ModelForm):
    # --- यह नया फील्ड सीट चुनने के लिए है ---
    seat_number = forms.ChoiceField(label="Seat Number")

    class Meta:
        model = Passenger
        fields = ['name', 'age', 'gender', 'seat_number']

    def __init__(self, *args, **kwargs):
        # सीट के चॉइस को व्यू से डायनामिक रूप से सेट करने के लिए
        available_seats = kwargs.pop('available_seats', [])
        super().__init__(*args, **kwargs)
        if available_seats:
            self.fields['seat_number'].choices = [(seat, seat) for seat in available_seats]


PassengerFormSet = formset_factory(PassengerForm, extra=0, can_delete=False)
