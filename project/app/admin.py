# Django
# First-Party
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from django.db.models.signals import post_save
from reversion.admin import VersionAdmin

# Local
from .forms import UserChangeForm
from .forms import UserCreationForm
from .inlines import AssignmentInline
from .models import Account
from .models import Assignment
from .models import Discussion
from .models import School
from .models import User
from .models import Voter
from .signals import account_post_save
from .tasks import privatize_account
from .tasks import send_moderation_email
from .tasks import send_unmoderation_email


def privatize(modeladmin, request, queryset):
    for account in queryset:
        privatize_account(account)
privatize.short_description = 'Privatize account'


def modulate_account(account):
    account.is_moderated = True
    post_save.disconnect(account_post_save, Account)
    account.save()
    post_save.connect(account_post_save, Account)
    send_moderation_email.delay(account)
    return



def modulate(modeladmin, request, queryset):
    for account in queryset:
        modulate_account(account)
modulate.short_description = 'Modulate account'

def unmodulate_account(account):
    account.is_moderated = False
    post_save.disconnect(account_post_save, Account)
    account.save()
    post_save.connect(account_post_save, Account)
    send_unmoderation_email.delay(account)
    return



def unmodulate(modeladmin, request, queryset):
    for account in queryset:
        unmodulate_account(account)
unmodulate.short_description = 'Unmodulate account'


@admin.register(Assignment)
class AssignmentAdmin(VersionAdmin):
    save_on_top = True
    fields = [
        'date',
        'account',
        'school',
    ]
    list_display = [
        'id',
        'date',
        'school',
        'account',
    ]
    list_editable = [
        'account',
    ]
    autocomplete_fields = [
        'account',
        'school',
    ]
    ordering = [
        'school',
    ]

@admin.register(Discussion)
class DiscussionAdmin(VersionAdmin):
    save_on_top = True
    fields = [
        'name',
        'date',
        'video',
    ]
    list_display = [
        'id',
        'name',
        'date',
    ]
    ordering = [
        'date',
    ]


@admin.register(Account)
class AccountAdmin(VersionAdmin):
    save_on_top = True
    fields = [
        'is_featured',
        'name',
        'email',
        'zone',
        'phone',
        'is_moderated',
        'is_public',
        'is_voter',
        'role',
        'comments',
        'sendgrid',
        'notes',
    ]
    list_display = [
        'name',
        'comments',
        'is_featured',
        'is_moderated',
        'is_public',
        'is_comment',
        'is_voter',
        'zone',
        'role',

    ]
    list_editable = [
    ]
    list_filter = [
        'is_moderated',
        'is_featured',
        'is_public',
        'is_voter',
        'role',
        'zone',
    ]
    search_fields = [
        'name',
        'email',
    ]
    autocomplete_fields = [
        'user',
    ]
    inlines = [
    ]
    ordering = [
        '-created',
    ]
    readonly_fields = [
        'is_comment',
    ]
    actions = [
        privatize,
        modulate,
        unmodulate,
    ]
    def is_comment(self, obj):
        return bool(obj.comments)
    is_comment.boolean = True


@admin.register(School)
class SchoolAdmin(VersionAdmin):
    save_on_top = True
    fields = [
        'name',
    ]
    list_display = [
        'name',
    ]
    list_editable = [
    ]
    list_filter = [
    ]
    search_fields = [
        'name',
    ]
    inlines = [
        AssignmentInline,
    ]
    autocomplete_fields = [
    ]


@admin.register(Voter)
class VoterAdmin(VersionAdmin):
    save_on_top = True
    fields = [
        'voter_id',
        'last_name',
        'first_name',
        'middle_name',
        'suffix',
        'age',
        'address',
        'city',
        'st',
        'zipcode',
        'zone',
    ]
    list_display = [
        'last_name',
        'first_name',
        'age',
        'zone',
    ]
    list_editable = [
    ]
    list_filter = [
        'zone',
    ]
    search_fields = [
        'first_name',
        'last_name',
    ]
    inlines = [
    ]
    ordering = [
        'last_name',
        'first_name',
    ]


@admin.register(User)
class UserAdmin(UserAdminBase):
    save_on_top = True
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    fieldsets = (
        (None, {
            'fields': [
                'username',
            ]
        }
        ),
        ('Data', {
            'fields': [
                'name',
                'email',
            ]
        }
        ),
        ('Permissions', {'fields': ('is_admin', 'is_active')}),
    )
    list_display = [
        # 'username',
        'name',
        'email',
        'created',
        'last_login'
    ]
    list_filter = [
        'is_active',
        'is_admin',
        'created',
        'last_login',
    ]
    search_fields = [
        'username',
        'name',
        'email',
    ]
    ordering = [
        '-created',
    ]
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': [
                'username',
                'is_admin',
                'is_active',
            ]
        }
        ),
    )
    filter_horizontal = ()
    inlines = [
    ]
    readonly_fields = [
        'name',
        # 'email',
    ]

# Use Auth0 for login
admin.site.login = staff_member_required(
    admin.site.login,
    login_url=settings.LOGIN_URL,
)
