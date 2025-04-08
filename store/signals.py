from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Customer



@receiver(post_save, sender=User)
def save_customer(sender, instance, **kwargs):
    instance.customer.save()
    
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_customer(sender, instance, created, **kwargs):
    if created:
        Customer.objects.get_or_create(user=instance)