# Django
from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

# Local
from . import views

urlpatterns = [
    # Root
    path('', views.index, name='index',),

    # Footer
    path('about/', TemplateView.as_view(template_name='app/pages/about.html'), name='about',),
    path('faq/', TemplateView.as_view(template_name='app/pages/faq.html'), name='faq',),
    path('privacy/', TemplateView.as_view(template_name='app/pages/privacy.html'), name='privacy',),
    path('terms/', TemplateView.as_view(template_name='app/pages/terms.html'), name='terms',),
    path('support/', TemplateView.as_view(template_name='app/pages/support.html'), name='support',),

    # Authentication
    path('join', views.join, name='join'),
    path('callback', views.callback, name='callback'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),

    # Account
    path('account', views.account, name='account',),

    # Delete
    path('delete', views.delete, name='delete',),

    # Share
    path('share', RedirectView.as_view(url='https://smilewestada.wistia.com/medias/2oyxggw7kp'), name='share'),

    # EMail
    path('sendgrid-event-webhook', views.sendgrid_event_webhook, name='webhook',),
]
