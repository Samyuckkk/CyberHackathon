from django.db import models
from django.contrib.auth.models import User
import base64

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




class ServerKeys(models.Model):
    """Stores the hospital server’s keypairs (Kyber + ECC)"""
    kyber_public = models.TextField()
    kyber_private = models.TextField()
    ecdh_public = models.TextField()
    ecdh_private = models.TextField()

    def __str__(self):
        return "Server Hybrid-PQC Keys"


class UserPublicKey(models.Model):
    """Stores each ambulance’s Dilithium (signature) public key"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dilithium_public = models.TextField()

    def __str__(self):
        return f"{self.user.username} keys"




class IntegrityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    merkle_root = models.CharField(max_length=128)
    payload = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
