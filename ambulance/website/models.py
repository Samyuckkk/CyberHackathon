from django.db import models
from django.contrib.auth.models import User

class Vitals(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ecg = models.CharField(max_length=100, default='--')
    spo2 = models.FloatField(default=0)
    nibp = models.CharField(max_length=50, default='--')  # e.g. "120/80"
    rr = models.FloatField(default=0)
    temp = models.FloatField(default=0)
    status = models.CharField(max_length=50, default='Stable')

    def __str__(self):
        return f"{self.user.username} Vitals"
    