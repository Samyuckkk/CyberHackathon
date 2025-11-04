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
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Vitals"
    

class AmbulanceStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {'Active' if self.is_active else 'Inactive'}"
