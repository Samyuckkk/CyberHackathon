from django.contrib.auth.models import Group, User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Vitals

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
