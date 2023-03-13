import uuid

import django_filters
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils.encoding import force_str, force_text
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Title


def send_email(request, user):
    email = EmailMessage(
        'Api_yambdb confirmation code',
        f"{user.username}, Ваш проверочный код {user.confirm_code}",
        settings.DEFAULT_FROM_EMAIL,
        [user.email, ]
    )
    email.send()


def generate_confirm_code():
    """Генератор проверочного кода."""
    return uuid.uuid4()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class CustomValidation(APIException):
    """Запилил кастомное исключение."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'A server error occurred.'

    def __init__(self, detail, field, status_code):
        if status_code is not None:
            self.status_code = status_code
        if detail is not None:
            self.detail = {field: force_str(detail)}
        else:
            self.detail = {'detail': force_text(self.default_detail)}


class TitleFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(field_name='genre__slug')
    category = django_filters.CharFilter(field_name='category__slug')

    class Meta:
        model = Title
        fields = ('name', 'genre', 'category', 'year')
