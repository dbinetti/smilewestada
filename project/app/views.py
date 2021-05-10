import json
import logging

import jwt
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as log_in
from django.contrib.auth import logout as log_out
from django.contrib.auth.decorators import login_required
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
from .models import Assignment

log = logging.getLogger('SMA')


# Root
def index(request):
    accounts = Account.objects.filter(
        is_public=True,
        user__is_active=True,
    ).order_by(
        '-is_featured',
        '-created',
    )
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
        'initScreen': 'signUp',
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
        'initScreen': 'login',
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
    log.info(payload)
    if not payload['email']:
        messages.error(
            request,
            "Email address is required",
        )
        return redirect('index')
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
            return redirect('share')
    else:
        form = AccountForm(instance=account)
    accounts = Account.objects.filter(
        is_public=True,
        user__is_active=True,
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

# Account
@login_required
def share(request):
    return render(
        request,
        'app/pages/share.html',
    )

@login_required
def sign(request):
    assignments = Assignment.objects.order_by(
        'school__name',
    )
    return render(
        request,
        'app/pages/sign.html',
        context = {
            'assignments': assignments,
        }
    )

@login_required
def updates(request):
    updates = [
        ('Update #1 - May 6', 'http://us7.campaign-archive.com/?u=2a7069bda2face16fe1e2674f&id=22b5bcef67'),
        ('Update #2 - May 7', 'http://us7.campaign-archive.com/?u=2a7069bda2face16fe1e2674f&id=c382811712'),
        ('Update #3 - May 8', 'http://us7.campaign-archive.com/?u=2a7069bda2face16fe1e2674f&id=b29f9c9a2c'),
        ('Update #4 - May 9', 'http://us7.campaign-archive.com/?u=2a7069bda2face16fe1e2674f&id=9b41dcc6cb'),
    ]
    return render(
        request,
        'app/pages/updates.html',
        context = {
            'updates': updates,
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
def sendgrid_event_webhook(request):
    if request.method == 'POST':
        payload_list = json.loads(request.body)
        for payload in payload_list:
            if payload['event'] == 'bounce':
                email = payload['email']
                log.error(f'Bounced Email: {email}')
                # deactivate_user.delay(email)
            else:
                log.info(f'Not a bounce: {payload}')
    return HttpResponse()
