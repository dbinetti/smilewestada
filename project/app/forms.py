# Django
from django import forms
from django.contrib.auth.forms import UserChangeForm as UserChangeFormBase
from django.contrib.auth.forms import UserCreationForm as UserCreationFormBase
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

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
            'is_volunteer',
            'comments',
            'notes',
        ]
        labels = {
            "is_public": "Make My Name Public",
            "is_volunteer": "Volunteer to Help",
        }
        widgets = {
            'comments': forms.Textarea(
                attrs={
                    'class': 'form-control h-25',
                    'placeholder': 'Any respectful, on-topic comments to share publicly? (Optional)',
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
            'name': "Please provide your real full name.  Your name remains private \
            unless you explicity ask to be Public.",
            'comments': "To leave a public comment, you must provide your real full \
            name.  Comments are optional, but will be hidden if a full name \
            is not provided.",
            'is_public': "Showing your support publicly encourages others to join \
            and enables you to make a comment below.",
            'is_volunteer': mark_safe("Want to do more?  We'll keep you updated on additional volunteer opportunities."),
            'zone': mark_safe("Please indicate your <a href='https://res.cloudinary.com/dyvz0sbfw/raw/upload/v1620230044/smilewestada/app/wasd_trustee_zones.20328492709b.pdf' target='_blank'>District Zone</a> so we can direct your \
            message to the proper Trustee."),
        }

    def clean_comments(self):
        comments= self.cleaned_data['comments']
        words = comments.split(" ")
        for word in words:
            if any([
                word.startswith("http"),
                word.startswith("www"),
            ]):
                raise ValidationError(
                    "Links are not allowed in comments."
                )
        return comments


    def clean(self):
        cleaned_data = super().clean()
        is_public = cleaned_data.get("is_public")
        comments = cleaned_data.get("comments")

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
