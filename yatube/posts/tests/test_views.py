from django import forms
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='some_user')

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.unauthorized_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """View-функция использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}):
                    'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.user.username}):
                    'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}):
                    'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}):
                    'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_user.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Контекст в шаблоне index соответствует ожидаемому."""
        response = self.unauthorized_user.get(reverse('posts:index'))
        expected = list(Post.objects.select_related('author', 'group'))
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_group_list_show_correct_context(self):
        """Контекст в шаблоне group_list соответствует ожидаемому."""
        response = self.unauthorized_user.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        expected = list(get_object_or_404(
            Group, slug=self.group.slug).posts.select_related('author'))
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_profile_show_correct_context(self):
        """Контекст в шаблоне profile соответствует ожидаемому."""
        response = self.unauthorized_user.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        expected = list(get_object_or_404(
            User, username=self.user.username).posts.select_related('group'))
        self.assertEqual(list(response.context['page_obj']), expected)

    def test_post_detail_show_correct_context(self):
        """Контекст в шаблоне post_detail соответствует ожидаемому."""
        response = self.unauthorized_user.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context.get('post'), self.post)

    def test_create_post_show_correct_context(self):
        """Контекст в шаблоне create_post соответствует ожидаемому."""
        namespace_list = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        ]
        for reverse_name in namespace_list:
            response = self.authorized_user.get(reverse_name)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.models.ModelChoiceField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_check_post_with_group_in_pages(self):
        """Проверка поста с группой на страницах index, group_list, profile."""
        pages_names = {
            reverse('posts:index'): Post.objects.get(group=self.post.group),
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): Post.objects.get(group=self.post.group),
            reverse(
                'posts:profile', kwargs={'username': self.user.username}
            ): Post.objects.get(group=self.post.group),
        }
        for value, expected in pages_names.items():
            with self.subTest(value=value):
                response = self.unauthorized_user.get(value)
                self.assertIn(expected, response.context['page_obj'])

    def test_check_post_with_group_not_on_wrong_page(self):
        """Проверка, что пост не попал в неверную группу."""
        pages_names = {
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): Post.objects.exclude(group=self.post.group),
        }
        for value, expected in pages_names.items():
            with self.subTest(value=value):
                response = self.unauthorized_user.get(value)
                self.assertNotIn(expected, response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    """Проверка пагинации на страницах."""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='some_user')

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug',
        )

        for post_number in range(13):
            cls.post = Post.objects.create(
                text=f'Тестовый пост {post_number}',
                author=cls.user,
                group=cls.group
            )

    def setUp(self):
        self.unauthorized_user = Client()

    def test_paginator(self):
        POSTS_ON_FIRST_PAGE = 10
        POSTS_ON_SECOND_PAGE = 3
        pages_names = {
            'posts:index': reverse('posts:index'),
            'posts:group_list': reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}),
            'posts:profile': reverse(
                'posts:profile', kwargs={'username': self.user.username}),
        }
        for page_name, reverse_name in pages_names.items():
            with self.subTest(page_name=page_name):
                self.assertEqual(len(self.unauthorized_user.get(
                    reverse_name).context['page_obj']),
                    POSTS_ON_FIRST_PAGE)
                self.assertEqual(len(self.unauthorized_user.get(
                    reverse_name + '?page=2').context['page_obj']),
                    POSTS_ON_SECOND_PAGE)
