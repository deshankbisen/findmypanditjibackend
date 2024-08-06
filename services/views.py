# services/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Panditji
from .models import Booking
import json,logging
from twilio.rest import Client
from twilio.rest import Client
import os
from django.conf import settings
from django.db import IntegrityError
from django.http import JsonResponse
TWILIO_ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
TWILIO_SERVICE_SID = settings.TWILIO_SERVICE_SID

@csrf_exempt  # Only use this for testing purposes
def register_panditji(request):
    if request.method == 'POST':
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        qualification = request.POST.get('qualification')
        speciality = request.POST.get('speciality')
        experience = request.POST.get('experience')
        city = request.POST.get('city')
        area = request.POST.get('area')
        mobile_number = request.POST.get('mobileNumber')
        first_name_part = first_name[:2]  # First two characters of the first name
        last_name_part = last_name[:2]    # First two characters of the last name
        mobile_number_part = mobile_number[:4]  # First four characters of the mobile number
        ids =mobile_number_part
        # File handling
        document = request.FILES.get('fileUpload')
        # Save the data to the database
        Panditji.objects.create(
            first_name=first_name,
            last_name=last_name,
            qualification=qualification,
            speciality=speciality,
            experience=experience,
            city=city,
            area=area,
            mobile_number=mobile_number,
            id=int(ids),
            document=document  # Make sure your model has a field for this      
        )

        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid method'}, status=405)

def get_unique_cities(request):
    if request.method == 'GET':
        cities = Panditji.objects.values_list('city', flat=True).distinct()
        return JsonResponse(list(cities), safe=False)
    
def get_unique_areas(request):
    city = request.GET.get('city', '')
    if city:
        areas = Panditji.objects.filter(city=city).values_list('area', flat=True).distinct()
        return JsonResponse(list(areas), safe=False)
    return JsonResponse([], safe=False)

def find_panditji_city(request):
    city = request.GET.get('city', '')
    # area = request.GET.get('area', '')

    if not city :
        return JsonResponse({'error': 'City is required'}, status=400)

    # Query the database for Pandit Jis based on city and area
    pandit_jis = Panditji.objects.filter(city__iexact=city)
    
    panditji_list = [
        {
            'first_name': panditji.first_name,
            'last_name': panditji.last_name,
            'experience': panditji.experience,
            'qualification': panditji.qualification,
            'speciality': panditji.speciality,
            'city': panditji.city,
            'id': panditji.id
                }
        for panditji in pandit_jis
    ]
        
    return JsonResponse(panditji_list, safe=False)

def find_panditji_area(request):
    city = request.GET.get('city', '')
    area = request.GET.get('area', '')

    if not city or not area:
        return JsonResponse({'error': 'City and area are required'}, status=400)

    # Query the database for Pandit Jis based on city and area
    pandit_jis = Panditji.objects.filter(city__iexact=city, area__iexact=area)
    
    panditji_list = [
        {
            'first_name': panditji.first_name,
            'last_name': panditji.last_name,
            'experience': panditji.experience,
            'qualification': panditji.qualification,
            'speciality': panditji.speciality,
            'city': panditji.city,
            'id': panditji.id
                }
        for panditji in pandit_jis
    ]
        
    return JsonResponse(panditji_list, safe=False)

@csrf_exempt
def book_panditji(request):
    print (TWILIO_AUTH_TOKEN)
    print (TWILIO_ACCOUNT_SID)
    if request.method == 'POST':
        data = json.loads(request.body)
        user_name = data.get('userName')
        address = data.get('address')
        date = data.get('date')
        time = data.get('time')
        pooja_type = data.get('poojaType')
        poojan_samagri = data.get('poojanSamagri')
        id=data.get('panditji')
        mobilenumber=data.get('mobilenumber')
        try:
            booking = Booking(
                user_name=user_name,
                address=address,
                date=date,
                time=time,
                pooja_type=pooja_type,
                poojan_samagri=poojan_samagri,
                panditji=Panditji.objects.get(id=id),
                mobilenumber=mobilenumber
            )
            booking.save()            
            account_sid = TWILIO_ACCOUNT_SID
            auth_token = 'a154a0062419ef94527acf90070ffb41'
            client = Client(account_sid, auth_token)

            message = client.messages.create(
            from_='+12085635105',
            body=f'Thanks for booking you Pooja with Panditji Shri {Panditji.objects.get(id=id)} schedulled on {date} we will reach out to you in a while over callf or confirmation.',
            to=mobilenumber
            )
            account_sid = TWILIO_ACCOUNT_SID
            auth_token = 'a154a0062419ef94527acf90070ffb41'
            client = Client(account_sid, auth_token)

            message = client.messages.create(
            from_='whatsapp:+14155238886',
            body=f'Thanks for booking you Pooja with Panditji Shri {Panditji.objects.get(id=id)} schedulled on {date} we will reach out to you in a while over callf or confirmation.',
            to=f'whatsapp:{mobilenumber}'
            )

            print(message.sid)

            return JsonResponse({'status': 'success', 'message': 'Booking successful'})
        except IntegrityError:
            return JsonResponse({'status': 'error', 'message': 'Booking already exists'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


