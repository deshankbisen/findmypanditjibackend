# services/urls.py
from django.urls import path
from .views import register_panditji
from . import views
from django.urls import path



urlpatterns = [
    path('register_panditji/', views.register_panditji, name='register_panditji'),
    path('get_unique_cities/', views.get_unique_cities, name='get_unique_cities'),
    path('get_unique_areas/', views.get_unique_areas, name='get_unique_areas'),
    path('find_panditji_city/', views.find_panditji_city, name='find_panditji_city'),
    path('find_panditji_area/', views.find_panditji_area, name='find_panditji_area'),
    path('book_panditji/', views.book_panditji, name='book_panditji'),
]
