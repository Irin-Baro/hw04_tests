from math import ceil
from random import randint

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group
from posts.forms import PostForm

User = get_user_model()


class PostViewTests(TestCase):
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

    def test_post_is_in_the_lists_of_posts(self):
        """Проверка контекста в шаблонах index, group_list и profile."""
        reverse_name_list = [
            (reverse('posts:index')),
            (reverse('posts:group_list', kwargs={'slug': self.group.slug})),
            (reverse('posts:profile', kwargs={
                'username': self.user.username}))
        ]
        for reverse_name in reverse_name_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.unauthorized_user.get(reverse_name)
                self.assertEqual(response.context['page_obj'][0], self.post)

    def test_post_detail_show_correct_context(self):
        """Контекст в шаблоне post_detail соответствует ожидаемому."""
        response = self.unauthorized_user.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context.get('post'), self.post)

    def test_create_post_show_correct_context(self):
        """Проверка корректности формы."""
        reverse_name_list = [
            (reverse('posts:post_create')),
            (reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        ]
        for reverse_name in reverse_name_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_user.get(reverse_name)
                self.assertIsInstance(response.context['form'], PostForm)

    def post_edit_page_shows_correct_post_in_form(self):
        """Проверка, что на странице редактирования в форме правильный пост"""
        response = self.authorized_user.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context.get('form').instance, self.post)

    def test_check_post_with_group_not_on_wrong_page(self):
        """Проверка, что пост не попал в неверную группу."""
        self.new_group = Group.objects.create(
            title='Новая группа',
            description='Описание новой группы',
            slug='new-slug',
        )
        reverse_name = reverse('posts:group_list', kwargs={
            'slug': self.new_group.slug})
        response = self.unauthorized_user.get(reverse_name)
        self.assertNotIn(self.post, response.context['page_obj'])


class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.number_of_posts = randint(1, 23)

        cls.user = User.objects.create_user(username='some_user')

        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug',
        )

        posts = (Post(
            text=f'Тестовый пост {post_number}',
            group=cls.group,
            author=cls.user,
        ) for post_number in range(cls.number_of_posts))
        Post.objects.bulk_create(posts)

        cls.reverse_name_list = [
            (reverse('posts:index')),
            (reverse('posts:group_list', kwargs={'slug': 'test-slug'})),
            (reverse('posts:profile', kwargs={
                'username': 'some_user'}))
        ]

    def setUp(self):
        self.unauthorized_user = Client()

    def test_paginator_on_first_page(self):
        """Проверка количества постов на первой странице."""
        if self.number_of_posts < settings.POST_PER_PAGE:
            posts_on_first_page = self.number_of_posts
        else:
            posts_on_first_page = settings.POST_PER_PAGE
        for reverse_name in self.reverse_name_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.unauthorized_user.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 posts_on_first_page)

    def test_paginator_on_last_page(self):
        """Проверка количества постов на последней странице."""
        last_page_number = ceil(self.number_of_posts
                                / settings.POST_PER_PAGE)
        if self.number_of_posts > settings.POST_PER_PAGE:
            if self.number_of_posts % settings.POST_PER_PAGE != 0:
                posts_on_last_page = (self.number_of_posts
                                      % settings.POST_PER_PAGE)
            else:
                posts_on_last_page = settings.POST_PER_PAGE
            for reverse_name in self.reverse_name_list:
                with self.subTest(reverse_name=reverse_name):
                    response = self.unauthorized_user.get(
                        reverse_name + f'?page={str(last_page_number)}')
                    self.assertEqual(len(response.context['page_obj']),
                                     posts_on_last_page)
