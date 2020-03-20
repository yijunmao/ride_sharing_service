from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Ride, Sharer
from django.core.validators import MinValueValidator


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length = 32, required = True, widget=forms.TextInput(attrs={'class':'form-control' , 'autocomplete': 'off','pattern':'[A-Za-z ]+', 'title':'Enter Characters Only '}))
    last_name = forms.CharField(max_length = 32, required = True, widget=forms.TextInput(attrs={'class':'form-control' , 'autocomplete': 'off','pattern':'[A-Za-z ]+', 'title':'Enter Characters Only '}))
    email = forms.EmailField(max_length = 256, required = True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'first_name', 'last_name',  'email', 'password1', 'password2']



class CreateViewForm(forms.ModelForm):
    def clean_max_allowed_persons(self):
        if self.cleaned_data['can_shared']:
            if self.cleaned_data['max_allowed_persons'] == None or self.cleaned_data['max_allowed_persons'] <= 0:
                raise forms.ValidationError("Please enter a number greater than zero!")
        return self.cleaned_data['max_allowed_persons']
    class Meta:
        model = Ride
        fields = ['dest_addr', 'arr_date_time', 'no_persons_owner', 'can_shared', 'max_allowed_persons',
                  'special_request', 'owner_vehicle_type']



class SharerForm(forms.ModelForm):
    class Meta:
        model = Sharer
        fields = ['dest_arr', 'earliest_time', 'latest_time', 'no_persons_sharer']



class SharerUpdateForm(forms.Form):
    no_of_persons = forms.IntegerField(label="Number of Persons", validators=[MinValueValidator(1)])




class DriverRegisterForm(forms.Form):
    license_no = forms.CharField(label="License Number", required=True)
    vehicle_type = forms.ChoiceField(label="Vehicle Type", choices=[("Sedan", "Sedan"), ("SUV", "SUV"), ("Coupe", "Coupe"), ("Convertible", "Convertible")], required=True)
    vehicle_make = forms.CharField(max_length=256, required=True, label="Make")
    plate_number = forms.CharField(max_length=256, required=True, label="Plate Number")
    vehicle_capacity = forms.IntegerField(required=True, label="Capacity", validators=[MinValueValidator(2)])
    special_vehicle_info = forms.CharField(label="Special Vehicle Info", required=False)
