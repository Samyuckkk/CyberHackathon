"""
URL configuration for ambulance project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('role-redirect/', views.role_redirect, name='role_redirect'),
    path('hospital-dashboard/', views.hospital_dash, name='hospital_dash'),
    path('ambulance-dashboard/', views.ambulance_dash, name='ambulance_dash'),
    path('api/update-vitals/', views.update_vitals, name='update_vitals'),
    path('api/get-vitals/', views.get_all_vitals, name='get_all_vitals'),
    path('api/server-keys/', views.get_server_keys, name='get_server_keys'),
    path('api/register-ambulance-key/', views.register_ambulance_key, name='register_ambulance_key'),
    path('api/update-vitals-secure/', views.update_vitals_secure, name='update_vitals_secure'),
]
