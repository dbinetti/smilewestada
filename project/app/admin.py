# Django
# First-Party
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.admin import UserAdmin as UserAdminBase
from fsm_admin.mixins import FSMTransitionMixin
from polymorphic.admin import PolymorphicChildModelAdmin
from polymorphic.admin import PolymorphicChildModelFilter
from polymorphic.admin import PolymorphicParentModelAdmin
from reversion.admin import VersionAdmin

# Local
from .forms import UserChangeForm
from .forms import UserCreationForm
from .inlines import AssignmentInline
from .inlines import AttendeeInline
from .models import Account
from .models import Assignment
from .models import Attendee
from .models import Comment
from .models import Event
from .models import School
from .models import SpokenComment
from .models import User
from .models import Voter
from .models import WrittenComment
from .tasks import moderate_account
from .tasks import privatize_account
from .tasks import reinstate_account


def privatize(modeladmin, request, queryset):
    for account in queryset:
        privatize_account(account)
privatize.short_description = 'Privatize Account'


def moderate(modeladmin, request, queryset):
    for account in queryset:
        moderate_account(account)
moderate.short_description = 'Moderate Account'


def reinstate(modeladmin, request, queryset):
    for account in queryset:
        reinstate_account(account)
reinstate.short_description = 'Reinstate Account'


@admin.register(Account)
class AccountAdmin(FSMTransitionMixin, VersionAdmin):
    fsm_field = [
        'state',
    ]
    save_on_top = True
    fields = [
        'state',
        'name',
        'zone',
        'is_public',
        'is_voter',
        'role',
        'sendgrid',
        'notes',
    ]
    list_display = [
        'name',
        'is_public',
        'is_voter',
        'zone',
        'role',
    ]
    list_editable = [
    ]
    list_filter = [
        'is_public',
        'is_voter',
        'role',
        'zone',
    ]
    search_fields = [
        'name',
        'user__email',
    ]
    autocomplete_fields = [
        'user',
    ]
    inlines = [
    ]
    ordering = [
        '-created',
    ]
    actions = [
        privatize,
        moderate,
        reinstate,
    ]

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


@admin.register(Comment)
class CommentAdmin(FSMTransitionMixin, PolymorphicParentModelAdmin, VersionAdmin):
    save_on_top = True
    fields = [
        # 'video',
        'state',
    ]
    fsm_fields = [
        'state',
    ]
    list_filter = [
        'state',
        PolymorphicChildModelFilter,
    ]
    list_display = [
        '__str__',
    ]
    ordering = [
        '-created',
    ]
    child_models = [
        WrittenComment,
        SpokenComment,
    ]
    autocomplete_fields = [
        'account',
    ]
    list_select_related = [
        'account',
    ]


@admin.register(WrittenComment)
class WrittenCommentAdmin(FSMTransitionMixin, PolymorphicChildModelAdmin, VersionAdmin):
    save_on_top = True
    fsm_fields = [
        'state',
    ]
    fields = [
        'state',
        'is_featured',
        'is_moderated',
        'account',
        'text',
    ]
    list_display = [
        'text',
    ]
    ordering = [
        '-created',
    ]
    autocomplete_fields = [
        'account',
    ]
    base_model = Comment


@admin.register(SpokenComment)
class SpokenCommentAdmin(PolymorphicChildModelAdmin, VersionAdmin):
    save_on_top = True
    fields = [
        'state',
        'account',
        'video',
    ]
    list_display = [
        'id',
    ]
    ordering = [
        '-created',
    ]
    autocomplete_fields = [
        'account',
    ]
    base_model = Comment


@admin.register(Event)
class EventAdmin(VersionAdmin):
    save_on_top = True
    fields = [
        'name',
        'date',
        'description',
        'location',
        'notes',
    ]
    list_display = [
        'name',
        'date',
        'location',
    ]
    list_editable = [
    ]
    list_filter = [
    ]
    search_fields = [
        'name',
    ]
    inlines = [
        AttendeeInline,
    ]
    autocomplete_fields = [
    ]


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
