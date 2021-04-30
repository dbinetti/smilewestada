# Django
from django import forms
from django.contrib.auth.forms import UserChangeForm as UserChangeFormBase
from django.contrib.auth.forms import UserCreationForm as UserCreationFormBase
from django.core.exceptions import ValidationError

# Local
from .models import Account
from .models import User


class DeleteForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
    )


class AccountForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Account
        fields = [
            'name',
            'zone',
            'phone',
            'email',
            'is_public',
            'comments',
            'notes',
        ]
        labels = {
            "is_public": "Make My Name Public",
        }
        widgets = {
            'comments': forms.Textarea(
                attrs={
                    'class': 'form-control h-25',
                    'placeholder': 'Any respectful, on-topic comments to share publicly? (Optional, Name Must Be Public)',
                    'rows': 5,
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control h-25',
                    'placeholder': 'Anything else we should know? (Optional, Private)',
                    'rows': 5,
                }
            )
        }
        help_texts = {
            'name': "Please provide your real name.  Your name remains private \
            unless you explicity ask to be Public.",
            'is_public': "Showing your support publicly encourages others to join.",
            'zone': "Please indicate your District Zone so we can direct your \
            message to the proper Board Member.",
        }


    def clean(self):
        cleaned_data = super().clean()
        is_public = cleaned_data.get("is_public")
        comments = cleaned_data.get("comments")
        name = cleaned_data.get("name")

        if comments and not is_public:
            raise ValidationError(
                "Comments are only shared if you make your name public."
            )


class UserCreationForm(UserCreationFormBase):
    """
    Custom user creation form for Auth0
    """

    # Bypass password requirement
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_unusable_password()
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = [
            'username',
        ]


class UserChangeForm(UserChangeFormBase):
    """
    Custom user change form for Auth0
    """

    class Meta:
        model = User
        fields = [
            'username',
        ]
