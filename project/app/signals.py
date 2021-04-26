from django.db.models.signals import post_save
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Account
from .models import User
from .tasks import create_account
from .tasks import delete_user
from .tasks import delete_user_email
from .tasks import send_confirmation
from .tasks import update_auth0
from .tasks import update_user_from_account


@receiver(pre_delete, sender=User)
def delete_auth0(sender, instance, **kwargs):
    delete_user(instance.username)
    delete_user_email(instance.email)
    return


@receiver(post_save, sender=Account)
def account_post_save(sender, instance, created, **kwargs):
    if created:
        return
    update_user_from_account.delay(instance)
    return

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    if created:
        create_account(instance)
        send_confirmation.delay(instance)
        return
    update_auth0.delay(instance)
    return
