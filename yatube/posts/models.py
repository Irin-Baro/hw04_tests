from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Group(models.Model):
    """Модель сообщества"""
    title = models.CharField(
        max_length=200,
        verbose_name='Название сообщества',
        help_text='Укажите название сообщества'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Уникальный фрагмент URL-адреса сообщества',
        help_text='Укажите уникальный фрагмент URL-адреса сообщества'
    )
    description = models.TextField(
        verbose_name='Описание сообщества',
        help_text='Здесь должно быть описание сообщества'
    )

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    def __str__(self):
        return self.title


class Post(models.Model):
    """Модель записи"""
    text = models.TextField(
        verbose_name='Текст записи',
        help_text='Разместите здесь текст'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор записи',
        help_text='Укажите имя автора записи'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Сообщество',
        help_text='Укажите название сообщества'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'

    def __str__(self):
        return self.text[:settings.NUMBER_OF_CHAR]
