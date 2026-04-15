from django.core import mail
from django.conf import settings
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from .models import Contact
import requests
import json
import re


def index(request):
    return render(request, 'index.html')


def contact(request):
    if request.method == "POST":
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        phone = request.POST.get('num')
        description = request.POST.get('description')

        contact_query = Contact(
            name=fullname,
            email=email,
            number=phone,
            description=description
        )
        contact_query.save()

        from_email = settings.EMAIL_HOST_USER
        connection = mail.get_connection()
        connection.open()

        email_mesge = mail.EmailMessage(
            f'Website Email from {fullname}',
            f'Email from : {email}\nUser Query : {description}\nPhone No : {phone}',
            from_email,
            ['ananthakrishnannairrs@gmail.com'],
            connection=connection
        )

        email_user = mail.EmailMessage(
            'ABC Company',
            f'Hello {fullname}\nThanks for contacting us. We will resolve your query as soon as possible.\nThank you.',
            from_email,
            [email],
            connection=connection
        )

        connection.send_messages([email_mesge, email_user])
        connection.close()

        messages.info(request, "Thanks for contacting us")
        return redirect('/contact')

    return render(request, 'contact.html')


def fetch_weather(city):
    city_query = city.replace(" ", "+")
    url = f"https://wttr.in/{city_query}?format=j1"

    response = requests.get(
        url,
        timeout=15,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    response.raise_for_status()

    data = response.json()
    current = data["current_condition"][0]
    nearest = data["nearest_area"][0]

    return {
        "region": nearest["areaName"][0]["value"],
        "country": nearest["country"][0]["value"],
        "temp_now": current["temp_C"],
        "feels_like": current["FeelsLikeC"],
        "humidity": current["humidity"],
        "wind_kmph": current["windspeedKmph"],
        "weather_now": current["weatherDesc"][0]["value"],
        "dayhour": current.get("localObsDateTime", "N/A"),
    }


def weather(request):
    result = None
    error = None

    if 'city' in request.GET:
        city = request.GET.get('city', '').strip()

        if city:
            try:
                result = fetch_weather(city)
            except Exception as e:
                error = str(e)

    return render(request, 'weather.html', {
        'result': result,
        'error': error,
    })


def extract_city_from_message(message):
    message = message.strip()

    patterns = [
        r'weather in ([a-zA-Z\s]+)',
        r'temperature in ([a-zA-Z\s]+)',
        r'forecast for ([a-zA-Z\s]+)',
        r'is it raining in ([a-zA-Z\s]+)',
        r'how is the weather in ([a-zA-Z\s]+)',
        r'([a-zA-Z\s]+) weather',
    ]

    for pattern in patterns:
        match = re.search(pattern, message.lower())
        if match:
            return match.group(1).strip().title()

    return None


def weather_chatbot(request):
    if request.method != "POST":
        return JsonResponse({"reply": "Only POST method is allowed."}, status=405)

    try:
        body = json.loads(request.body)
        user_message = body.get("message", "").strip()

        if not user_message:
            return JsonResponse({"reply": "Please type a question."})

        lower_msg = user_message.lower()

        if any(word in lower_msg for word in ["hi", "hello", "hey"]):
            return JsonResponse({
                "reply": "Hello! Ask me things like: 'weather in Chennai' or 'temperature in Delhi'."
            })

        if "help" in lower_msg:
            return JsonResponse({
                "reply": "You can ask: weather in Mumbai, temperature in Kolkata, forecast for Hyderabad."
            })

        city = extract_city_from_message(user_message)

        if city:
            try:
                weather_data = fetch_weather(city)
                reply = (
                    f"Current weather in {weather_data['region']}, {weather_data['country']} is "
                    f"{weather_data['temp_now']}°C with {weather_data['weather_now']}. "
                    f"It feels like {weather_data['feels_like']}°C, humidity is {weather_data['humidity']}%, "
                    f"and wind speed is {weather_data['wind_kmph']} km/h."
                )
                return JsonResponse({"reply": reply})
            except Exception:
                return JsonResponse({
                    "reply": f"Sorry, I could not fetch weather data for '{city}'. Please try another city."
                })

        return JsonResponse({
            "reply": "I am a weather chatbot. Ask something like 'weather in Chennai' or 'temperature in Delhi'."
        })

    except Exception as e:
        return JsonResponse({"reply": f"Error: {str(e)}"}, status=500)


def handleBlog(request):
    if not request.user.is_authenticated:
        messages.error(request, "Please login and try again")
        return redirect('/login')
    return render(request, 'handleBlog.html')


def about(request):
    return render(request, 'about.html')


def signUp(request):
    if request.method == "POST":
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        if pass1 != pass2:
            return HttpResponse("Password not matched")

        try:
            if User.objects.get(username=username):
                return HttpResponse("Username is taken")
        except User.DoesNotExist:
            pass

        try:
            if User.objects.get(email=email):
                return HttpResponse("Email is already taken")
        except User.DoesNotExist:
            pass

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = firstname
        myuser.last_name = lastname
        myuser.save()

        messages.success(request, "Signup successfully")
        return redirect('/login')

    return render(request, 'auth/signUp.html')


def handlelogin(request):
    if request.method == "POST":
        handleusername = request.POST['username']
        handlepassword = request.POST['pass1']
        user = authenticate(username=handleusername, password=handlepassword)

        if user is not None:
            login(request, user)
            messages.info(request, 'Welcome to my website')
            return redirect('/')
        else:
            messages.warning(request, "Invalid credentials")
            return redirect('/login')

    return render(request, 'auth/login.html')


def handlelogout(request):
    logout(request)
    messages.success(request, "Logout success")
    return redirect('/login')