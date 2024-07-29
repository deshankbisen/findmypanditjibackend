# services/urls.py
from django.urls import path
from .views import register_panditji
from . import views


urlpatterns = [
    path('register_panditji/', views.register_panditji, name='register_panditji'),
    path('get_unique_cities/', views.get_unique_cities, name='get_unique_cities'),
    path('get_unique_areas/', views.get_unique_areas, name='get_unique_areas'),
    path('find_panditji/', views.find_panditji, name='find_panditji'),
    path('book_panditji/', views.book_panditji, name='book_panditji'),

]
