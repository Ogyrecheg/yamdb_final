from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

ROLES = (
    ('user', 'Пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор'),
    ('superuser', 'Суперюзер'),
)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(
        "биография",
        blank=True
    )
    role = models.TextField(
        "роль",
        blank=True,
        choices=ROLES,
        default='user',
    )
    confirm_code = models.UUIDField(
        verbose_name='проверочный код',
        blank=True,
        null=True,
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name='стать админом'
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name='стать суперюзером'
    )
    is_moderator = models.BooleanField(
        default=False,
        verbose_name='стать модератором'
    )


class Genre(models.Model):
    name = models.CharField(
        "жанр",
        max_length=256,
        help_text="напишите название жанра"
    )
    slug = models.SlugField(
        "слаг",
        unique=True,
        help_text="придумайте короткое уникальное имя жанра"
    )

    def __str__(self):
        return f'{self.name} {self.slug}'


class Category(models.Model):
    name = models.CharField(
        "категория",
        max_length=256,
        help_text="напишите название категории"
    )
    slug = models.SlugField(
        "слаг",
        unique=True,
        help_text="придумайте короткое уникальное имя категории"
    )

    def __str__(self):
        return f'{self.name} {self.slug}'


class Title(models.Model):
    name = models.CharField(
        "произведение",
        max_length=256,
        help_text="напишите название произведения"
    )
    description = models.TextField(
        "описание",
        help_text="напишите краткое описание группы",
        blank=True
    )
    year = models.IntegerField(
        "год создания произведения",
        help_text="напишете год создания произведения"
    )
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenre',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='title'
    )

    def __str__(self):
        return self.name


class TitleGenre(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.CharField(
        max_length=2000
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )

    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        ),
        error_messages={'validators': 'Оценка может быть только от 1 до 10'}
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique review'
            )]
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.CharField(
        verbose_name='Текст комментария',
        max_length=1000
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )

    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]
