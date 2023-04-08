from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_user = User.objects.create_user(username='author_user')
        cls.another_user = User.objects.create_user(username='another_user')

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug',
        )

        cls.post = Post.objects.create(
            author=cls.author_user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.unauthorized_user = Client()
        self.post_author = Client()
        self.post_author.force_login(self.author_user)
        self.authorized_user = Client()
        self.authorized_user.force_login(self.another_user)

    def test_url_status_code_for_unauthorized_user(self):
        """Проверка доступности страниц для неавторизованных пользователей."""
        status_codes_for_urls = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.author_user}/': HTTPStatus.OK,
            f'/posts/{self.post.id}': HTTPStatus.OK,
            '/create/': HTTPStatus.FOUND,
            f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for address, response_code in status_codes_for_urls.items():
            with self.subTest(address=address):
                self.assertEqual(
                    self.unauthorized_user.get(address).status_code,
                    response_code
                )

    def test_url_status_code_for_authorized_user(self):
        """Проверка доступности страниц для авторизованных пользователей."""
        status_codes_for_urls = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.author_user}/': HTTPStatus.OK,
            f'/posts/{self.post.id}': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for address, response_code in status_codes_for_urls.items():
            with self.subTest(address=address):
                self.assertEqual(
                    self.authorized_user.get(address).status_code,
                    response_code
                )

    def test_url_status_code_for_post_author(self):
        """Проверка доступности страниц для авторизованных авторов."""
        status_codes_for_urls = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.author_user}/': HTTPStatus.OK,
            f'/posts/{self.post.id}': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            f'/posts/{self.post.id}/edit/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for address, response_code in status_codes_for_urls.items():
            with self.subTest(address=address):
                self.assertEqual(
                    self.post_author.get(address).status_code,
                    response_code
                )

    def test_url_redirect(self):
        """Проверка редиректов на другую страницу"""
        self.assertRedirects(
            self.unauthorized_user.get(
                '/create/', follow=True),
            '/auth/login/?next=/create/'
        )
        self.assertRedirects(
            self.unauthorized_user.get(
                f'/posts/{self.post.id}/edit/', follow=True),
            f'/auth/login/?next=/posts/{self.post.id}/edit/'
        )
        self.assertRedirects(
            self.authorized_user.get(
                f'/posts/{self.post.id}/edit/', follow=True),
            f'/posts/{self.post.id}'
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.author_user}/': 'posts/profile.html',
            f'/posts/{self.post.id}': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.post_author.get(address)
                self.assertTemplateUsed(response, template)
