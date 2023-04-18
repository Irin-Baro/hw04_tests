import tempfile
import shutil

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings

from posts.models import Post, Group

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='post_author')
        cls.another_user = User.objects.create_user(username='new_post_author')

        cls.group = Group.objects.create(
            title='Заголовок группы',
            description='Описание группы',
            slug='test-slug',
        )

        cls.another_group = Group.objects.create(
            title='Заголовок другой группы',
            description='Описание другой группы',
            slug='another-slug',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_new_post(self):
        """Проверка создания новой записи."""
        self.authorized_user.force_login(self.another_user)
        Post.objects.all().delete()
        form_data = {
            'text': 'Новый пост',
            'group': self.group.id,
        }
        response = self.authorized_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        posts_count_after_test = Post.objects.count()
        expected_posts_number = 1
        if posts_count_after_test == expected_posts_number:
            new_post = Post.objects.get()
        self.assertEqual(posts_count_after_test, expected_posts_number)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.author, self.another_user)
        self.assertEqual(new_post.group_id, form_data['group'])
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.another_user.username}))

    def test_edit_post(self):
        """Проверка редактирования записи."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Измененный текст',
            'group': self.another_group.id,
        }
        response = self.authorized_user.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)
        post = Post.objects.get(id=self.post.id)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.group_id, form_data['group'])
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
