from django.contrib.auth.models import Group, User
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import Vitals, AmbulanceStatus

@receiver(post_save, sender=User)
def add_user_to_group(sender, instance, created, **kwargs):
    if created:
        # Example: check username pattern or a custom field
        if instance.username.lower().startswith("ambulance"):
            group, _ = Group.objects.get_or_create(name="ambulance")
            instance.groups.add(group)

            Vitals.objects.create(user=instance)

        elif instance.username.lower().startswith("hospital"):
            group, _ = Group.objects.get_or_create(name="hospital")
            instance.groups.add(group)


@receiver(user_logged_in)
def set_ambulance_active(sender, user, request, **kwargs):
    if user.groups.filter(name='ambulance').exists():
        status, _ = AmbulanceStatus.objects.get_or_create(user=user)
        status.is_active = True
        status.save()

@receiver(user_logged_out)
def set_ambulance_inactive(sender, user, request, **kwargs):
    if user.groups.filter(name='ambulance').exists():
        status, _ = AmbulanceStatus.objects.get_or_create(user=user)
        status.is_active = False
        status.save()