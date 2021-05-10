
# Django
from django.contrib import admin

# Local
from .models import Assignment


class AssignmentInline(admin.TabularInline):
    model = Assignment
    fields = [
        'date',
        'account',
        'school',
    ]
    readonly_fields = [
    ]
    ordering = (
    )
    show_change_link = True
    extra = 0
    classes = [
        # 'collapse',
    ]
    autocomplete_fields = [
        'account',
        'school',
    ]
