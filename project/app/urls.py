# Django
from django.urls import path
from django.views.generic import TemplateView

# Local
from . import views

urlpatterns = [
    # Root
    path('', views.index, name='index',),

    # Footer
    path('about/', TemplateView.as_view(template_name='app/pages/about.html'), name='about',),
    path('updates/', views.updates, name='updates',),
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
    path('events', views.events, name='events',),
    path('event/<str:event_id>', views.event, name='event',),
    # path('sign/', views.sign, name='sign',),

    # Share
    # path('share', views.share, name='share'),


    # Comments
    path('comments', views.comments, name='comments',),
    path('comment/<str:comment_id>/delete', views.comment_delete, name='comment-delete',),
    path('comment/submit-written', views.submit_written_comment, name='submit-written-comment'),
    path('comment/submit-spoken', views.submit_spoken_comment, name='submit-spoken-comment'),
    path('comment/video-submission', views.video_submission, name='video-submission'),

    # Delete
    path('delete', views.delete, name='delete',),

    # EMail
    path('sendgrid-event-webhook', views.sendgrid_event_webhook, name='webhook',),
]
