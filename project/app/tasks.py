# Standard Libary
import csv
import logging

# First-Party
from auth0.v3.authentication import GetToken
from auth0.v3.management import Auth0
# Django
from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.template.loader import render_to_string
from django_rq import job
from fuzzywuzzy import fuzz
from mailchimp3 import MailChimp
from mailchimp3.helpers import get_subscriber_hash
from mailchimp3.mailchimpclient import MailChimpError

from .forms import VoterForm
from .models import Account
from .models import User
from .models import Voter

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


@job
def update_auth0_from_user(user):
    if not user.username.startswith('auth0|'):
        return
    client = get_auth0_client()
    payload = {
        'name': user.name,
        'email': user.email,
    }
    response = client.users.update(user.username, payload)
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
def create_or_update_mailchimp_from_account(account):
    client = get_mailchimp_client()
    list_id = settings.MAILCHIMP_AUDIENCE_ID
    email = account.user.email
    subscriber_hash = get_subscriber_hash(email)
    zone = account.zone if account.zone else 0
    data = {
        'status_if_new': 'subscribed',
        'email_address': email,
        'merge_fields': {
            'NAME': account.name,
            'COMMENTS': account.comments,
            'ZONE': zone,
            'PUBLIC': int(account.is_public),
            'VOLUNTEER': int(account.is_volunteer),
        }
    }
    try:
        client.lists.members.create_or_update(
            list_id=list_id,
            subscriber_hash=subscriber_hash,
            data=data,
        )
    except MailChimpError as err:
        # error = json.loads(str(e).replace("\'", "\""))
        # if error['title'] == 'Invalid Resource':
        #     user = User.objects.get(
        #         email=email,
        #     )
        #     user.is_active = False
        #     user.save()
        #     result = 'Invalid Resource'
        # else:
        #     raise e
        raise err
    return

@job
def create_mailchimp_from_account(account):
    client = get_mailchimp_client()
    list_id = settings.MAILCHIMP_AUDIENCE_ID
    data = {
        'status': 'subscribed',
        'email_address': account.user.email,
    }
    client.lists.members.create(
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
    if not account.comments:
        return
    email = build_email(
        template='app/emails/update.txt',
        subject=f'SWA {count}',
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

@job
def send_fullname_email(account):
    email = build_email(
        template='app/emails/fullname.txt',
        subject='Smile West Ada - Real, Full Name Notice',
        from_email='David Binetti <dbinetti@smilewestada.com>',
        to=[account.user.email],
    )
    return email.send()

@job
def send_moderation_email(account):
    email = build_email(
        template='app/emails/modulate.txt',
        subject='Smile West Ada - On Topic Notice',
        from_email='David Binetti <dbinetti@smilewestada.com>',
        to=[account.user.email],
    )
    return email.send()

@job
def send_unmoderation_email(account):
    email = build_email(
        template='app/emails/unmoderate.txt',
        subject='Smile West Ada - Comments Reinstated',
        from_email='David Binetti <dbinetti@smilewestada.com>',
        to=[account.user.email],
    )
    return email.send()

@job
def deactivate_user(email):
    user = User.objects.get(email=email)
    user.is_active = False
    user.save()
    return


def import_voters(filename):
    with open(filename) as f:
        reader = csv.reader(
            f,
            skipinitialspace=True,
        )
        next(reader)
        rows = [row for row in reader]
        t = len(rows)
        i = 0
        errors = []
        output = []
        for row in rows:
            i += 1
            print(f"{i}/{t}")
            voter = {
                'voter_id': int(row[0]),
                'prefix': row[2].strip(),
                'last_name': row[2].strip(),
                'first_name': row[3].strip(),
                'middle_name': row[4].strip(),
                'suffix': row[1].strip(),
                'age': int(row[6]),
                'address': row[8].strip(),
                'city': row[10].strip(),
                'st': 'ID',
                'zipcode': row[12].strip(),
                'zone': int(row[27][-1]),
            }
            form = VoterForm(voter)
            if form.is_valid():
                output.append(voter)
    return output


def voter_names():
    cache_key = 'voter_names'
    value = cache.get(cache_key)
    if not value:
        vs = Voter.objects.all()
        value = [f'{v.first_name} {v.last_name}' for v in vs]
        cache.set(cache_key, value, 86000)
    return value

def match_names(account, min_score=0, invalidate=False):
    cache_key = 'voter_names'
    voters = cache.get(cache_key)
    if not voters or invalidate:
        vs = Voter.objects.all()
        voters = [f'{v.first_name} {v.last_name}'.lower() for v in vs]
        cache.set(cache_key, voters, 86000)
    max_score = -1
    # max_name = ''
    account_name = account.name.lower()
    for voter in voters:
        score = fuzz.partial_ratio(account_name, voter)
        if (score > min_score) & (score > max_score):
            max_name = voter
            max_score = score
    if max_score == 100:
        from app.signals import account_post_save
        account.is_voter = True
        post_save.disconnect(account_post_save, Account)
        account.save()
        post_save.connect(account_post_save, Account)
        return 'matched'
    else:
        return (max_score, max_name, account_name)

# @job
# def voter_verify(account):
#     vs = Voter.objects.all()
#     voters = [f'{v.first_name} {v.last_name}' for v in vs]
#     for voter in voters:

#     return
