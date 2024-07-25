# services/forms.py
from django import forms
from .models import Panditji

class PanditjiForm(forms.ModelForm):
    class Meta:
        model = Panditji
        fields = [
            'first_name', 'last_name', 'qualification', 
            'speciality', 'experience', 'city', 
            'area', 'mobile_number', 'document'
        ]
