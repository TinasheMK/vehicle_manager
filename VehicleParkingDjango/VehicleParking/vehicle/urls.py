# from django.contrib import admin
from django.urls import path
from .import views

urlpatterns =[
    path('',views.Index),
    path('admin_login',views.admin_login)
]
