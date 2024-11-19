from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import User
import logging
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save

logger = logging.getLogger('users')

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    roles = ["Student", "Teacher", "Admin"]
    for role in roles:
        group, created = Group.objects.get_or_create(name=role)

        if role == "Admin":
            all_permissions = Permission.objects.all()
            group.permissions.set(all_permissions)
            group.save()

    print("Default groups created successfully.")


@receiver(post_save, sender=User)
def log_user_registration(sender, instance, created, **kwargs):
    if created:
        logger.info(f"New user registered: {instance.username}")

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    logger.info(f"User logged in: {user.username}")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    logger.info(f"User logged out: {user.username}")

