from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    username = models.CharField(
        "Имя пользователя",
        max_length=150,
        unique=True,
        help_text="Обязательное, не более 150 символов",
        validators=[UnicodeUsernameValidator()],
        error_messages={"unique": "Пользователь с таким именем уже существует."},
    )
    email = models.EmailField(
        "Почта",
        max_length=150,
        unique=True,
        help_text="Обязательное, не более 150 символов",
    )
    first_name = models.CharField(
        "Имя",
        max_length=150,
        help_text="Обязательное, не более 150 символов",
    )
    last_name = models.CharField(
        "Фамилия",
        max_length=150,
        help_text="Обязательное, не более 150 символов",
    )
    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to="avatars/",
        blank=True,
        null=True,
        help_text="Загрузите ваш аватар",
    )
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        help_text="The groups this user belongs to.",
        related_name="custom_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="custom_user_set",
        related_query_name="user",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("username", "first_name", "last_name")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("username",)
        db_table = "users_user"

    def __str__(self):
        return self.username


class Subscription(models.Model):
    "Модель для подписок",
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=("user", "author"), name="unique_name_following"
            )
        ]

    def __str__(self):
        return f"{self.user} подписан на {self.author}"
