from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import DestroyAPIView, ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from reviews.models import Category, Genre, Review, Title, User

from .permissions import (AdminPermission, AdminPlusPermission,
                          IsAuthorAndStaffOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleGETSerializer, TitleSerializer, TokenSerializer,
                          UserSerializer)
from .utils import (CustomValidation, TitleFilter, generate_confirm_code,
                    get_tokens_for_user, send_email)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('genre',)
    permission_classes = (IsAuthenticatedOrReadOnly, )
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return TitleGETSerializer
        return TitleSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return super().get_permissions()
        return (AdminPermission(),)


class MixinViewSet(ListCreateAPIView, DestroyAPIView, GenericViewSet):
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = (AdminPlusPermission, )
    lookup_field = 'slug'
    lookup_value_regex = '[^/]+'


class GenreViewSet(MixinViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CategoryViewSet(MixinViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@permission_classes([AllowAny])
def sign_up(request):
    """Вью функция регистранции пользователя и выдачи confirm_code."""

    serializer = SignUpSerializer(data=request.data)
    try:
        if serializer.is_valid(raise_exception=True):
            user, created = User.objects.get_or_create(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email']
            )
            user.confirm_code = generate_confirm_code()
            user.save()
            send_email(request, user)

            return Response(serializer.data, status=status.HTTP_200_OK)
    except IntegrityError:
        raise CustomValidation(
            'Пользователь с данным email уже зарегистрирован.',
            'email',
            status_code=status.HTTP_400_BAD_REQUEST
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_func(request):
    """Вью функция выдачи JWT токена пользователю."""

    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid():
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username'],
            confirm_code=serializer.validated_data['confirm_code'],
        )
        jwt = get_tokens_for_user(user)

        return Response(jwt['access'], status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter, )
    search_fields = ('username', )
    permission_classes = (AdminPermission,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        url_name='me',
        serializer_class=UserSerializer,
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request):
        """Обновленние, получение данных пользователя."""

        user_me = request.user
        serializer = self.get_serializer(user_me)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user_me, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(
                    username=user_me.username,
                    email=user_me.email,
                    role=user_me.role
                )

                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST
                            )

        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorAndStaffOrReadOnly, ]

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'),
            title__id=self.kwargs.get("title_id"))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorAndStaffOrReadOnly, ]

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return Review.objects.filter(title=self.get_title().id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())
