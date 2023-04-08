from django.contrib.auth import get_user_model
from django.test import TestCase
from django.conf import settings

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='some_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(
            self.post.text[:settings.NUMBER_OF_CHAR], str(self.post)
        )
        self.assertEqual(self.group.title, str(self.group))

    def test_post_verbose_name(self):
        """Verbose_name в полях совпадает с ожидаемым в моделе Post."""
        field_verboses = {
            'text': 'Текст записи',
            'pub_date': 'Дата публикации',
            'author': 'Автор записи',
            'group': 'Сообщество',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(
                        field).verbose_name, expected_value)

    def test_group_verbose_name(self):
        """Verbose_name в полях совпадает с ожидаемым в моделе Group."""
        field_verboses = {
            'title': 'Название сообщества',
            'slug': 'Уникальный фрагмент URL-адреса сообщества',
            'description': 'Описание сообщества',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(
                        field).verbose_name, expected_value)

    def test_post_help_text(self):
        """Help_text в полях совпадает с ожидаемым в моделе Post."""
        field_help_texts = {
            'text': 'Разместите здесь текст',
            'author': 'Укажите имя автора записи',
            'group': 'Укажите название сообщества',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value)

    def test_group_help_text(self):
        """Help_text в полях совпадает с ожидаемым в моделе Group."""
        field_help_texts = {
            'title': 'Укажите название сообщества',
            'slug': 'Укажите уникальный фрагмент URL-адреса сообщества',
            'description': 'Здесь должно быть описание сообщества',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(
                        field).help_text, expected_value)
