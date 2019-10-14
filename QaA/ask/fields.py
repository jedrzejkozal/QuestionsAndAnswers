import re
from difflib import SequenceMatcher

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator, validate_password)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


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


class NumbersValidator:

    def validate(self, password, user=None):
        if self.has_numbers(password):
            return None
        raise ValidationError([
            ValidationError(
                _("Password must contain at least one number"),
                code="numbers")
        ])

    def has_numbers(self, string):
        return any(c.isdigit() for c in string)

    def get_help_text(self):
        return _("Password must contain at least one number")


class SimilarityValidator(UserAttributeSimilarityValidator):

    def validate(self, password, user=None):
        if not user:
            return

        for attribute_name in self.user_attributes:
            try:
                value = user[attribute_name]
            except KeyError:
                continue
            self.check_if_attribute_is_too_similar(
                password, attribute_name, value)

    def check_if_attribute_is_too_similar(self, password, attribute_name, value):
        value_parts = re.split(r'\W+', value) + [value]
        for value_part in value_parts:
            if SequenceMatcher(a=password.lower(), b=value_part.lower()).quick_ratio() >= self.max_similarity:
                raise ValidationError(
                    _("The password is too similar to the %(verbose_name)s"),
                    code='password_too_similar',
                    params={'verbose_name': attribute_name},
                )


class PasswordField(forms.CharField):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.password_validators = [
            SpecialCharactersValidator(), NumbersValidator()]

    def validate(self, value):
        super().validate(value)
        try:
            validate_password(
                value, password_validators=self.password_validators)
        except ValidationError as e:
            raise forms.ValidationError(str(e))
