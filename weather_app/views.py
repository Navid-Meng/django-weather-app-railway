from django.shortcuts import render, HttpResponse, redirect
import requests
from django.http import JsonResponse
from .models import City
from django.contrib import messages

# Create your views here.

def home(request):

    # Define api key and the base url for openweathermap
    API_KEY = '105267ddaa34bc74646e07b1e90a63a1'
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}'

    # Check if the request is a POST (when adding a new city)
    if request.method == 'POST':
        city_name = request.POST.get('city') # Get the city name from the form

        # Fetch weather data for the city from the API
        response = requests.get(url.format(city_name, API_KEY)).json()

        # Check if the city exists in the API
        if response['cod'] == 200:
            if not City.objects.filter(name=city_name).exists():
                # Save the new city to the database
                City.objects.create(name=city_name)
                messages.success(request, f'{city_name} has been added successfully!')
            else:
                messages.info(request, f'{city_name} already exists!')
        else:
            messages.error(request, f'City "{city_name}" not found!')

        return redirect('home')


    weather_data = []
    # Fetch weather data for all saved cities
    try:
        cities = City.objects.all() # Get all cities from the database
        for city in cities:
            response = requests.get(url.format(city.name, API_KEY))
            data = response.json()

            if data['cod'] == 200:
                city_weather = {
                    'city': city.name,
                    'temperature': data['main']['temp'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon']
                }
                weather_data.append(city_weather)
            else:
                City.objects.filter(name=city.name).delete()

    except requests.RequestException as e:
        print('Error connecting to weather service. Please try again later.')

    context = {'weather_data': weather_data}

    return render(request, 'index.html', context)