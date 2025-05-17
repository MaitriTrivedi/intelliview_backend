from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@receiver(pre_save, sender=User)
def ensure_email_set(sender, instance, **kwargs):
    """
    Ensure email is set for new users.
    """
    if not instance.email and instance.username:
        instance.email = instance.username 