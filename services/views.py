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
from datetime import datetime, timedelta
logger = logging.getLogger(__name__)
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
        mobile_number_part = mobile_number[3:7]  # First four characters of the mobile number
        username =first_name_part + mobile_number_part + last_name_part
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
            username=username,
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
            'username': panditji.username
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
            'username': panditji.username
                }
        for panditji in pandit_jis
    ]
        
    return JsonResponse(panditji_list, safe=False)

@csrf_exempt
def book_panditji(request):
    if request.method == 'POST':
        try:
            # Print raw request data
            print(f"Raw request data: {request.body}")

            # Parse JSON request data
            data = json.loads(request.body)

            # Extract data from the request
            data = json.loads(request.body)
            user_name = data.get('userName')
            address = data.get('address')
            date = data.get('date')
            time = data.get('time')
            duration_hours = data.get('duration')
            pooja_type = data.get('poojaType')
            poojan_samagri = data.get('poojanSamagri')
            username=data.get('panditji')
            mobilenumber=data.get('mobilenumber')
        # Print extracted data for debugging
            print(f"Extracted data: user_name={user_name}, address={address}, date={date}, time={time}, duration_hours={duration_hours}, pooja_type={pooja_type}, poojan_samagri={poojan_samagri}, username={username}, mobilenumber={mobilenumber}")

            # Validate required fields
            if not all([user_name, address, date, time, duration_hours, pooja_type, username, mobilenumber]):
                return JsonResponse({'status': 'error', 'message': 'Missing required fields.'}, status=400)

            # Convert date and time to datetime objects
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d').date()
                time_obj = datetime.strptime(time, '%H:%M').time()  # Parse AM/PM time
                duration_hours = int(duration_hours) + 1# Convert duration_hours to integer
            except ValueError as e:
                logger.error(f"Date/Time conversion error: {e}")
                return JsonResponse({'status': 'error', 'message': 'Invalid date or time format.'}, status=400)
            # Calculate start and end datetime
            start_datetime = datetime.combine(date_obj, time_obj)
            end_datetime = start_datetime + timedelta(hours=duration_hours)
            # Retrieve the PanditJi instance\
            print(start_datetime,end_datetime)
            try:
                panditji = Panditji.objects.get(username=username)
            except Panditji.MultipleObjectsReturned:
                return JsonResponse({'status': 'error', 'message': 'Multiple PanditJi objects found. Please contact support.'}, status=500)
            except Panditji.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'PanditJi not found. Please check the ID and try again.'}, status=404)

            # Check for overlapping bookings
            overlapping_bookings = Booking.objects.filter(
                panditji=panditji,
                date__lte=end_datetime.date(),
                date__gte=start_datetime.date()
            )
            print(overlapping_bookings)

            conflicts = []
            for booking in overlapping_bookings:
                existing_start_datetime = datetime.combine(booking.date, booking.time)
                existing_end_datetime = existing_start_datetime + timedelta(hours=booking.duration_hours)
                print(start_datetime,end_datetime,existing_start_datetime,existing_end_datetime)
                # Check for overlap
                if (start_datetime < existing_end_datetime and end_datetime > existing_start_datetime):
                    conflicts.append({
                        'start': existing_start_datetime.strftime('%Y-%m-%d %H:%M'),
                        'end': existing_end_datetime.strftime('%Y-%m-%d %H:%M')
                    })

            if conflicts:
                return JsonResponse({
                    'status': 'error',
                    'message': f'PanditJi is already booked for the selected time slot.{conflicts}',
                    'conflicting_slots': conflicts
                }, status=400)
            # Create a new booking
            booking = Booking(
                user_name=user_name,
                address=address,
                date=date_obj,
                time=time_obj,
                duration_hours=duration_hours,
                pooja_type=pooja_type,
                poojan_samagri=poojan_samagri,
                panditji=panditji,
                mobilenumber=mobilenumber
            )

            booking.save()
            account_sid = 'ACd474217efe2b2d5d95b95241b2368e83'
            auth_token = 'e39eead11782386f70263cec0e6642f1'
            client = Client(account_sid, auth_token)

            message = client.messages.create(
            from_='+12085635105',
            body=f'Thanks for booking you Pooja with Panditji Shri {Panditji.objects.get(username=username)} schedulled on {date} we will reach out to you in a while over callf or confirmation.',
            to=mobilenumber
            )
            if poojan_samagri:
                message = client.messages.create(
                from_='+12085635105',
                body=f'Mr. {booking.user_name} has booked the {booking.pooja_type} with you on {booking.date} at {booking.time} with poojan samagri',
                to=panditji.mobile_number
                )
            else:
                message = client.messages.create(
                from_='+12085635105',
                body=f'Mr. {booking.user_name} has booked the {booking.pooja_type} with you on {booking.date} at {booking.time} without poojan samagri',
                to=panditji.mobile_number
                )
                


            print(message.sid)
            response = {
                'status': 'success',
                'message': f"Booking for {booking.user_name} with {booking.panditji} on {booking.date} at {booking.time} was successful."
            }
            return JsonResponse(response)
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

