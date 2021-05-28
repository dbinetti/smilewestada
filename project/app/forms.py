# Django
from django import forms
from django.contrib.auth.forms import UserChangeForm as UserChangeFormBase
from django.contrib.auth.forms import UserCreationForm as UserCreationFormBase
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

# Local
from .models import Account
from .models import Attendee
from .models import Comment
from .models import SpokenComment
from .models import User
from .models import Voter
from .models import WrittenComment


class DeleteForm(forms.Form):
    confirm = forms.BooleanField(
        required=True,
    )


class WrittenCommentForm(forms.ModelForm):
    class Meta:
        model = WrittenComment
        fields = [
            'text',
        ]
        widgets = {
            'text': forms.Textarea(
                attrs={
                    'class': 'form-control h-25',
                    'placeholder': 'Any respectful, on-topic comments to share publicly? (Optional)',
                    'rows': 5,
                }
            ),
        }

class SpokenCommentForm(forms.ModelForm):
    class Meta:
        model = SpokenComment
        fields = [
            'video',
        ]

# class CommentForm(forms.ModelForm):
#     class Meta:
#         model = Comment
#         fields = [
#             'text',
#             'video',
#         ]
#         widgets = {
#             'text': forms.Textarea(
#                 attrs={
#                     'class': 'form-control h-25',
#                     'placeholder': 'Any respectful, on-topic comments to share publicly? (Optional)',
#                     'rows': 5,
#                 }
#             ),
#         }

class AttendeeForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = [
            'is_confirmed',
            # 'account',
            # 'event',
        ]
        labels = {
            "is_confirmed": "Yes I'll Attend",
        }

class VoterForm(forms.ModelForm):
    class Meta:
        model = Voter
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

class AccountForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Account
        fields = [
            'name',
            'zone',
            'role',
            'is_public',
            'is_voter',
            'notes',
        ]
        labels = {
            "is_public": "Make My Name Public",
            "is_voter": "I'm a Registered Voter",
        }
        widgets = {
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
            'is_public': "Showing your support publicly encourages others to join \
            and enables you to make a comment below.",
            'is_voter': "We'll verify with Ada County Elections and add a Badge to your Account.",
            'zone': mark_safe("Select your <a href='https://res.cloudinary.com/dyvz0sbfw/raw/upload/v1620230044/smilewestada/app/wasd_trustee_zones.20328492709b.pdf' target='_blank'>District Zone</a>."),
            'role': "Select the role that best describes you.  If both a parent and teacher, choose teacher.",
        }

    # def clean_comments(self):
    #     comments= self.cleaned_data['comments']
    #     words = comments.split(" ")
    #     for word in words:
    #         if any([
    #             word.startswith("http"),
    #             word.startswith("www"),
    #         ]):
    #             raise ValidationError(
    #                 "Links are not allowed in comments."
    #             )
    #     return comments


    def clean(self):
        cleaned_data = super().clean()
        is_public = cleaned_data.get("is_public")
        # comments = cleaned_data.get("comments")
        name = cleaned_data.get("name")
        last_name = name.partition(" ")[2]
        full_name = False
        if last_name:
            if len(last_name) > 1:
                full_name = True
        if is_public and not full_name:
            raise ValidationError(
                "You must provide your full, real name to be public."
            )
        # if comments and not is_public:
        #     raise ValidationError(
        #         "Comments are only shared if you make your name public."
        #     )


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
