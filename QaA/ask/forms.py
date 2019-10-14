from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class UsernameField(forms.CharField):

    def validate(self, value):
        super().validate(value)
        queryset = User.objects.filter(username=value)
        if len(queryset) != 0:
            raise forms.ValidationError("Username already taken")


class EmailField(forms.EmailField):

    def validate(self, value):
        super().validate(value)
        queryset = User.objects.filter(email=value)
        if len(queryset) != 0:
            raise forms.ValidationError("Email address already taken")


from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class SpecialCharactersValidator:
    special_characters = ['@', '!', '#', '$', '%', '^', '&', '*', ]

    def validate(self, password, user=None):
        for c in self.special_characters:
            if c in password:
                return None
        raise ValidationError([
            ValidationError(
                _("Password must contain at least one special character"),
                code="special_characters")
        ])

    def get_help_text(self):
        return _("Password must contain one special characters {}".format(self.special_characters))


class PasswordField(forms.CharField):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.password_validators = [SpecialCharactersValidator(), ]

    def validate(self, value):
        super().validate(value)
        try:
            validate_password(
                value, password_validators=self.password_validators)
        except ValidationError as e:
            raise forms.ValidationError(str(e))


class SignUpForm(forms.Form):
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)
    username = UsernameField(max_length=20, required=True)
    password = PasswordField(min_length=6, required=True,
                             error_messages={"min_length": "Password to short. Must be at least 6 characters long"})
    password_repeat = forms.CharField(min_length=6, required=True)
    email = EmailField(required=True)

    def clean_password_repeat(self):
        try:
            password = self.cleaned_data['password']
            password_repeat = self.cleaned_data['password_repeat']
        except KeyError:
            return None

        if password != password_repeat:
            raise forms.ValidationError('Password does not match')
        return password_repeat
