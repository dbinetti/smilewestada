# Standard Libary
import csv
import json
import logging

import requests
# First-Party
from auth0.v3.authentication import GetToken
from auth0.v3.exceptions import Auth0Error
from auth0.v3.management import Auth0
# Django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django_rq import job
from mailchimp3 import MailChimp
from mailchimp3.helpers import get_subscriber_hash
from mailchimp3.mailchimpclient import MailChimpError

from .models import Account
from .models import User

log = logging.getLogger('SMA')

# Auth0
def get_auth0_token():
    get_token = GetToken(settings.AUTH0_TENANT)
    token = get_token.client_credentials(
        settings.AUTH0_CLIENT_ID,
        settings.AUTH0_CLIENT_SECRET,
        f'https://{settings.AUTH0_TENANT}/api/v2/',
    )
    return token

def get_auth0_client():
    token = get_auth0_token()
    client = Auth0(
        settings.AUTH0_TENANT,
        token['access_token'],
    )
    return client

def get_auth0_user(user_id):
    client = get_auth0_client()
    data = client.users.get(user_id)
    return data

@job
def delete_auth0_user(user_id):
    client = get_auth0_client()
    response = client.users.delete(user_id)
    return response

# Account Creation Utility
def create_account_from_user(user):
    account = Account.objects.create(
        user=user,
        name=user.name,
        email=user.email,
    )
    return account


# Mailchimp
def get_mailchimp_client():
    enabled = not settings.DEBUG
    return MailChimp(
        mc_api=settings.MAILCHIMP_API_KEY,
        enabled=enabled,
    )


@job
def create_mailchimp_from_account(account):
    client = get_mailchimp_client()
    list_id = settings.MAILCHIMP_AUDIENCE_ID
    data = {
        'status': 'subscribed',
        'email_address': account.user.email,
    }
    result = client.lists.members.create(
        list_id=list_id,
        data=data,
    )
    return


@job
def delete_mailchimp_from_account(account):
    client = get_mailchimp_client()
    subscriber_hash = get_subscriber_hash(account.user.email)
    client = MailChimp(mc_api=settings.MAILCHIMP_API_KEY)
    try:
        client.lists.members.delete(
            list_id=settings.MAILCHIMP_AUDIENCE_ID,
            subscriber_hash=subscriber_hash,
        )
    except MailChimpError as err:
        log.error(err)
    return


# Utility
def build_email(template, subject, from_email, context=None, to=[], cc=[], bcc=[], attachments=[], html_content=None):
    body = render_to_string(template, context)
    if html_content:
        html_rendered = render_to_string(html_content, context)
    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=from_email,
        to=to,
        cc=cc,
        bcc=bcc,
    )
    if html_content:
        email.attach_alternative(html_rendered, "text/html")
    for attachment in attachments:
        with attachment[1].open() as f:
            email.attach(attachment[0], f.read(), attachment[2])
    return email

@job
def send_email(email):
    return email.send()


# Template Emails
@job
def send_welcome_email(account):
    email = build_email(
        template='app/emails/welcome.txt',
        subject='Welcome to Smile West Ada!',
        from_email='David Binetti <dbinetti@smilewestada.com>',
        context={'account': account},
        to=[account.user.email],
    )
    return email.send()

@job
def send_goodbye_email(email_address):
    email = build_email(
        template='app/emails/goodbye.txt',
        subject='Smile West Ada - Account Deleted',
        from_email='David Binetti <dbinetti@smilewestada.com>',
        to=[email_address],
    )
    return email.send()

@job
def send_admin_notification(account):
    count = Account.objects.all().count()
    email = build_email(
        template='app/emails/update.txt',
        subject='SWA Update',
        from_email='David Binetti <dbinetti@smilewestada.com>',
        context={'account': account, 'count': count},
        to=['dbinetti@gmail.com'],
    )
    return email.send()

@job
def send_planning_email(account):
    email = build_email(
        template='app/emails/planning.txt',
        subject='Smile West Ada - Planning Session Tonight, Monday May 3',
        from_email='David Binetti <dbinetti@smilewestada.com>',
        to=[account.user.email],
    )
    return email.send()

@job
def send_shutdown_email(account):
    email = build_email(
        template='app/emails/final.txt',
        subject='Smile West Ada - Shutdown Notice',
        from_email='David Binetti <dbinetti@smilewestada.com>',
        to=[account.user.email],
    )
    return email.send()
