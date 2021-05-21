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
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import AccountForm
from .forms import AttendeeForm
from .forms import CommentForm
from .forms import DeleteForm
from .models import Account
from .models import Assignment
from .models import Attendee
from .models import Comment
from .models import Event
from .tasks import get_mailchimp_client

log = logging.getLogger('SWA View')


# Root
def index(request):
    accounts = Account.objects.filter(
        is_public=True,
        user__is_active=True,
    ).order_by(
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
    next_url = request.GET.get('next', '/account')
    state = f"{get_random_string()}|{next_url}"
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
    next_url = request.GET.get('next', '/account')
    state = f"{get_random_string()}|{next_url}"
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
    print(browser_state, server_state)
    if browser_state != server_state:
        return HttpResponse(status=400)
    next_url = server_state.partition('|')[2]
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
    if not 'email' in payload:
        messages.error(
            request,
            "Email address is required",
        )
        return redirect('logout')
    user = authenticate(request, **payload)
    if user:
        log_in(request, user)
        if user.is_admin:
            return redirect('admin:index')
        return redirect(next_url)
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
            return redirect('account')
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

def comments(request):
    comments = Comment.objects.filter(
        account__is_public=True,
        state__gt=Comment.STATE.new,
        account__user__is_active=True,
    ).select_related(
        'account',
        'account__user',
    ).order_by(
        '-state',
        '-created',
    )
    return render(
        request,
        'app/pages/comments.html',
        context={
            'comments': comments,
        }
    )

@login_required
def submit(request):
    if request.POST:
        form = CommentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('comments')
    form = CommentForm()
    return render(
        request,
        'app/pages/submit.html',
        context={
            'form': form,
        }
    )


# @login_required
def sign(request):
    assignments = Assignment.objects.filter(
        date='2021-05-11',
    ).order_by(
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
def events(request):
    events = Event.objects.filter(
    ).order_by(
        'date',
    )
    return render(
        request,
        'app/pages/events.html',
        context = {
            'events': events,
        }
    )

@login_required
def event(request, event_id):
    event = get_object_or_404(
        Event,
        pk=event_id,
    )
    attendees = event.attendees.filter(
        is_confirmed=True,
    ).order_by(
        '-created',
    )
    try:
        attendee = event.attendees.get(account=request.user.account)
    except Attendee.DoesNotExist:
        attendee = None
    if request.method == 'POST':
        form = AttendeeForm(request.POST, instance=attendee)
        if form.is_valid():
            attendee = form.save(commit=False)
            attendee.account = request.user.account
            attendee.event = event
            attendee.save()
            messages.success(
                request,
                'Saved!',
            )
            return redirect('event', event_id)
    form = AttendeeForm(instance=attendee)
    return render(
        request,
        'app/pages/event.html',
        context = {
            'event': event,
            'attendees': attendees,
            'form': form,
        }
    )

@login_required
def updates(request):
    client = get_mailchimp_client()
    updates = client.campaigns.all(
        folder_id='ca56599381',
        sort_field='send_time',
    )['campaigns']
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
            if payload['event'] in ['bounce', 'dropped']:
                email = payload['email']
                try:
                    account = Account.objects.get(
                        user__email=email,
                    )
                except Account.DoesNotExist:
                    log.error(payload)
                    return HttpResponse()
                account.sendgrid = payload
                account.save()
    return HttpResponse()


@csrf_exempt
@require_POST
def comment_submission(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        comment = Comment(
            account=request.user.account,
        )
        comment.video.name = payload['public_id']
        comment.save()
    return HttpResponse()
