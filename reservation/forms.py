# reservation/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import formset_factory
from .models import CustomUser, Passenger, Booking

class CustomUserCreationForm(UserCreationForm):
    # ... (इसमें कोई बदलाव नहीं)
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

class BusSearchForm(forms.Form):
    # ... (इसमें कोई बदलाव नहीं)
    source = forms.CharField(label="From", required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter source city'}))
    destination = forms.CharField(label="To", required=True, widget=forms.TextInput(attrs={'placeholder': 'Enter destination city'}))

# --- यह नया फॉर्म फ़ोन नंबर के लिए जोड़ा गया है ---
class BookingDetailsForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['phone_number']
        widgets = {
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter contact number'}),
        }

class PassengerForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ['name', 'age', 'gender']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'age': forms.NumberInput(attrs={'placeholder': 'Age'}),
        }

PassengerFormSet = formset_factory(PassengerForm, extra=0, can_delete=False)
