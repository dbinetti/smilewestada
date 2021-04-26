import csv
import json

import jwt
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as log_in
from django.contrib.auth import logout as log_out
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.db import transaction
from django.http import HttpResponse
# from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import AccountForm
from .forms import DeleteForm
from .models import Account
from .models import User
from .tasks import account_update
from .tasks import create_auth0_user
from .tasks import send_email


# Root
def index(request):
    accounts = Account.objects.filter(
        is_public=True,
    ).order_by('-created')
    total = Account.objects.count()
    return render(
        request,
        'app/pages/index.html',
        {'accounts': accounts, 'total': total,},
    )

# Authentication
def join(request):
    redirect_uri = request.build_absolute_uri(reverse('callback'))
    state = f"{get_random_string()}"
    request.session['state'] = state
    params = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'response_type': 'code',
        'scope': 'openid profile email',
        'state': state,
        'redirect_uri': redirect_uri,
        'screen_hint': 'signup',
    }
    url = requests.Request(
        'GET',
        f'https://{settings.AUTH0_DOMAIN}/authorize',
        params=params,
    ).prepare().url
    return redirect(url)

def login(request):
    redirect_uri = request.build_absolute_uri(reverse('callback'))
    state = f"{get_random_string()}"
    request.session['state'] = state
    params = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'response_type': 'code',
        'scope': 'openid profile email',
        'state': state,
        'redirect_uri': redirect_uri,
        'prompt': 'login',
    }
    url = requests.Request(
        'GET',
        f'https://{settings.AUTH0_DOMAIN}/authorize',
        params=params,
    ).prepare().url
    return redirect(url)

def callback(request):
    # Reject if state doesn't match
    browser_state = request.session.get('state')
    server_state = request.GET.get('state')
    if browser_state != server_state:
        return HttpResponse(status=400)

    # Get Auth0 Code
    code = request.GET.get('code', None)
    if not code:
        return HttpResponse(status=400)
    token_url = f'https://{settings.AUTH0_DOMAIN}/oauth/token'
    redirect_uri = request.build_absolute_uri(reverse('callback'))
    token_payload = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'client_secret': settings.AUTH0_CLIENT_SECRET,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_uri,
    }
    token = requests.post(
        token_url,
        json=token_payload,
    ).json()
    payload = jwt.decode(
        token['id_token'],
        options={
            'verify_signature': False,
        }
    )
    payload['username'] = payload.pop('sub')
    user = authenticate(request, **payload)
    if user:
        log_in(request, user)
        if user.is_admin:
            return redirect('admin:index')
        return redirect('account')
    return HttpResponse(status=403)

def logout(request):
    log_out(request)
    params = {
        'client_id': settings.AUTH0_CLIENT_ID,
        'return_to': request.build_absolute_uri(reverse('index')),
    }
    logout_url = requests.Request(
        'GET',
        f'https://{settings.AUTH0_DOMAIN}/v2/logout',
        params=params,
    ).prepare().url
    messages.success(
        request,
        "You Have Been Logged Out!",
    )
    return redirect(logout_url)

# Account
@login_required
def account(request):
    account = request.user.account
    if request.POST:
        form = AccountForm(request.POST, instance=account)
        if form.is_valid():
            account = form.save()
            messages.success(
                request,
                "Saved!",
            )
            account_update.delay(account)
            return redirect('account')
    else:
        form = AccountForm(instance=account)
    accounts = Account.objects.filter(
        is_public=True,
    ).order_by('-created')
    total = Account.objects.count()
    return render(
        request,
        'app/pages/account.html',
        context={
            'form': form,
            'accounts': accounts,
            'total': total,
        },
    )

# Delete
@login_required
def delete(request):
    if request.method == "POST":
        form = DeleteForm(request.POST)
        if form.is_valid():
            user = request.user
            user.delete()
            messages.error(
                request,
                "Account Deleted!",
            )
            return redirect('index')
    else:
        form = DeleteForm()
    return render(
        request,
        'app/pages/delete.html',
        {'form': form,},
    )


@csrf_exempt
@require_POST
@transaction.atomic
def inbound(request):
    form = EmailForm(request.POST)
    if form.is_valid():
        email = form.save(commit=False)
        try:
            user = User.objects.get(
                email=email.from_email,
            )
        except User.DoesNotExist:
            user = None
        email.kind = email.KIND.inbound
        email.user = user
        email.save()
        email = EmailMessage(
            subject='KAN Inbound',
            body=f'{email.from_email}\n{email.subject}\n{email.text}',
            from_email='inbound@smilewestada.com',
            to=['dbinetti@gmail.com'],
        )
        send_email.delay(email)
        return HttpResponse(status=200)
    raise Exception(form.errors)


@csrf_exempt
@require_POST
@transaction.atomic
def wistia(request):
    data = json.loads(request.body)
    create_auth0_user(
        name=data['events'][0]['payload']['name'],
        email=data['events'][0]['payload']['email'],
    )
    return HttpResponse(status=200)
