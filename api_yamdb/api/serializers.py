import datetime
import re

from api.utils import CustomValidation
from django.core.exceptions import ValidationError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.validators import UniqueTogetherValidator
from reviews.models import Category, Comment, Genre, Review, Title, User


class GenreCategoryMeta:
    exclude = ('id',)
    lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta(GenreCategoryMeta):
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    class Meta(GenreCategoryMeta):
        model = Category


class TitleGETSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')

    def get_rating(self, obj):
        title = Review.objects.filter(title__name=obj)
        rating_dct = title.aggregate(Avg('score'))
        return rating_dct['score__avg']


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(), slug_field='slug', many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug'
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category',)
        read_only_fields = ('id', 'rating')

    def validated_year(self, value):
        if value > int(datetime.datetime.now().year):
            raise serializers.ValidationError(
                'Указан неверный год'
            )
        return value


class SignUpSerializer(serializers.Serializer):
    """
    Сериализатор регистрации нового пользователя,
    выдачи проверочного кода на email.
    """

    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)

    def validate_email(self, email):
        """Валидация email регуляркой."""

        regex = re.compile(
            r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
        )
        if not re.fullmatch(regex, email):
            raise serializers.ValidationError('Недопустимые символы email')

        return email

    def validate_username(self, username):
        """Валидация username регуляркой."""

        if not re.match(r'^[a-zA-Z0-9-_]+$', username):
            raise serializers.ValidationError('Недопустимые символы username.')

        if re.match(r'^me', username):
            raise serializers.ValidationError('Недопустимый username.')

        return username


class TokenSerializer(serializers.Serializer):
    """Сериализатор выдачи токена пользователю."""

    username = serializers.CharField(max_length=150, required=True)
    confirm_code = serializers.UUIDField(required=True)

    def validate_username(self, username):
        if re.match(r'me', username):
            return serializers.ValidationError(
                'Недопустимое имя пользователя!'
            )

        if not User.objects.filter(username=username).exists():
            raise CustomValidation(
                'Данный пользователь не зарегистрирован.',
                'username',
                status_code=status.HTTP_404_NOT_FOUND)

        if not re.match(r'^[a-zA-Z0-9]+$', username):
            raise serializers.ValidationError('Недопустимые символы username')

        return username

    def validate_confirm_code(self, confirm_code):
        if not User.objects.filter(confirm_code=confirm_code).exists():
            raise serializers.ValidationError('Данный confirm_code нет в БД.')

        return confirm_code

    def validate(self, data):
        if not User.objects.filter(
                confirm_code=data['confirm_code'],
                username=data['username']
        ).exists():
            raise serializers.ValidationError(
                'Данная пара username + confirm_code не зарегистрирована.'
            )

        return data


class ReviewCommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = "__all__"


class ReviewSerializer(ReviewCommentSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    class Meta(ReviewCommentSerializer.Meta):
        model = Review

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
                request.method == 'POST'
                and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError('Вы уже оставили отзыв на это произведение')
        return data


class CommentSerializer(ReviewCommentSerializer):
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )

    class Meta(ReviewCommentSerializer.Meta):
        model = Comment


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User для работы эндпоинта users (под админа)."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('username', 'email')
            )
        ]

    def validate_username(self, username):
        if not re.match(r'^[a-zA-Z0-9-_]+$', username):
            raise serializers.ValidationError('Недопустимые символы username')

        return username

    def validate_email(self, email):
        regex = re.compile(
            r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
        )
        if not re.fullmatch(regex, email):
            raise serializers.ValidationError('Недопустимые символы email')

        return email
