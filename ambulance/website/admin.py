from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import IntegrityLog
admin.site.register(IntegrityLog)

# hospital@gmail.com -> hospital@pass123
# ambulance1@gmail.com -> ambu1@pass123
# ambulance2@gmail.com -> ambu2@pass123