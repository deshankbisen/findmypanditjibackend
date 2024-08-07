# services/admin.py
from django.contrib import admin
from .models import Panditji,Booking


@admin.register(Panditji)
class PanditjiAdmin(admin.ModelAdmin):
    list_display = ('username','first_name', 'last_name', 'qualification', 'speciality', 'experience', 'city', 'area', 'mobile_number')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'panditji', 'date', 'time', 'pooja_type')
    search_fields = ('user_name', 'panditji__first_name', 'panditji__last_name', 'pooja_type')
    
