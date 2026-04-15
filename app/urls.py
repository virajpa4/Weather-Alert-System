from django.contrib import admin
from django.urls import path, include
from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('contact', views.contact, name='contact'),
    path('about', views.about, name='about'),
    path('handleBlog', views.handleBlog, name='handleBlog'),
    path('weather', views.weather, name='weather'),
    path('weather-chatbot/', views.weather_chatbot, name='weather_chatbot'),
    path('signUp', views.signUp, name='signUp'),
    path('login', views.handlelogin, name='handlelogin'),
    path('logout', views.handlelogout, name='handlelogout'),
]