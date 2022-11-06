import os
import shutil
import tempfile
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Page
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from http import HTTPStatus
from ..models import Post, Group, User, Follow
from ..forms import PostForm, CommentForm


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTest(TestCase):
    """Posts app views test-class."""

    POSTS_COUNT: int = 27
    COUNT_PAGE_POSTS: int = 10

    @classmethod
    def setUpClass(cls):
        """Makes class-fixtures for tests of posts app views."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.second_user = User.objects.create_user(username='second_user')
        cls.third_user = User.objects.create_user(username='third_user')
        Follow.objects.create(user=cls.user, following=cls.third_user)
        cls.group = Group.objects.create(
            title='test group 1',
            description='test group 1 description',
            slug='first_test_group'
        )
        objs = [
            Post(
                id=i,
                text=f'Это текст поста {i} из {cls.POSTS_COUNT}',
                author=cls.user,
                group=cls.group
            )
            for i in range(1, cls.POSTS_COUNT + 1)
        ]
        cls.posts = Post.objects.bulk_create(objs=objs)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.post_image = cls.posts[0]
        cls.post_image.image = SimpleUploadedFile(
            name='small_gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post_image.save()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def check_common_views_templates(cls, test_obj):
        """Checking common views templates with different settings."""
        common_views_templates = [
            ('posts:index', None, 'posts/index.html'),
            ('posts:group_list', cls.group.slug, 'posts/group_list.html'),
            ('posts:profile', cls.user.username, 'posts/profile.html'),
            ('posts:post_detail', cls.posts[0].id, 'posts/post_detail.html'),
        ]

        for namespace, args, template in common_views_templates:
            with test_obj.subTest(namespace=namespace, template=template):
                if args:
                    args = [args]
                url = reverse(namespace, args=args)
                response = test_obj.client.get(url)
                test_obj.assertTemplateUsed(
                    response,
                    template,
                    (f'View-функция {namespace} должна использовать '
                     f'шаблон {template}')
                )

    def setUp(self) -> None:
        """Set test settings."""
        cache.clear()
        self.client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(PostsViewsTest.user)

    def test_views_using_correct_templates_guest(self):
        """Test-function: View uses correct template for guest."""
        PostsViewsTest.check_common_views_templates(self)

        auth_views = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', args=[PostsViewsTest.posts[0].id]),
            reverse('posts:add_comment', args=[PostsViewsTest.posts[0].id]),
            reverse('posts:follow_index'),
            reverse(
                'posts:profile_follow', args=[PostsViewsTest.user.username]
            ),
            reverse(
                'posts:profile_unfollow', args=[PostsViewsTest.user.username]
            ),
        ]

        login_url = reverse('users:login')

        for url in auth_views:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    f'{login_url}?next={url}',
                    msg_prefix=('Гость должен направлятся на '
                                'страницу авторизации')
                )

    def test_views_using_correct_templates_authorized_client(self):
        """Test-function: View uses correct template for authorized client."""
        self.client.force_login(PostsViewsTest.user)
        PostsViewsTest.check_common_views_templates(self)
        auth_views = [
            (
                reverse('posts:post_create'),
                'posts/create_post.html'
            ),
            (
                reverse('posts:post_edit', args=[PostsViewsTest.posts[0].id]),
                'posts/create_post.html'
            ),
            (
                reverse('posts:follow_index'),
                'posts/follow.html'
            ),
        ]

        for url, template in auth_views:
            with self.subTest(url=url, template=template):
                response = self.client.get(url)
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Страница {url} не использует шаблон {template}'
                )

    def test_views_context(self):
        """Test-function: context is correct."""
        views_context_list = [
            (
                reverse('posts:index'),
                {'page_obj': Page}
            ),
            (
                reverse('posts:group_list', args=[PostsViewsTest.group.slug]),
                {'page_obj': Page, 'group': Group}
            ),
            (
                reverse('posts:profile', args=[PostsViewsTest.user.username]),
                {'page_obj': Page, 'author': User, 'following': bool}
            ),
            (
                reverse(
                    'posts:post_detail', args=[PostsViewsTest.posts[0].id]
                ),
                {'post': Post, 'comment_form': CommentForm, 'page_obj': Page}
            ),
            (
                reverse('posts:post_edit', args=[PostsViewsTest.posts[0].id]),
                {'form': PostForm, 'is_edit': bool}
            ),
            (
                reverse('posts:post_create'),
                {'form': PostForm, 'is_edit': bool}
            ),
            (
                reverse('posts:follow_index'),
                {'page_obj': Page}
            ),
        ]

        for url, context in views_context_list:
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                for field_name, field_type in context.items():
                    self.assertIn(
                        field_name,
                        response.context,
                        (f'Контекст для страницы {url} '
                         f'должен содержать поле {field_name}')
                    )
                    self.assertIsInstance(
                        response.context[field_name],
                        field_type,
                        (f'Значение в поле контекст {field_name} '
                         f'должно иметь тп значения {field_type}')
                    )

    def test_pagination(self):
        """Test-function: pagination is correct."""
        namespaces_list = [
            ('posts:index', []),
            ('posts:group_list', [PostsViewsTest.group.slug]),
            ('posts:profile', [PostsViewsTest.user.username]),
        ]

        for namespace, args in namespaces_list:
            url = reverse(namespace, args=args)
            on_page = PostsViewsTest.COUNT_PAGE_POSTS
            count = PostsViewsTest.POSTS_COUNT

            for i in range(count // on_page + 1):
                page_url = f'{url}?page={i + 1}'
                response = self.auth_client.get(page_url)

                with self.subTest(page_url=page_url):
                    page_obj = response.context['page_obj']
                    expected_count = min(count - on_page * i, on_page)
                    self.assertEqual(
                        len(page_obj.object_list),
                        expected_count,
                        (f'Количество постов на странице {url} '
                         f'отличается от ожидаемого')
                    )

    def test_view_display_new_post(self):
        """Test-function: view display new post."""
        new_user = User.objects.create_user(username='new_user')
        new_group = Group.objects.create(
            title='test new group',
            description='test new group description',
            slug='new_test_group'
        )
        new_post = Post.objects.create(
            text='Это текст поста примеси',
            author=new_user,
            group=new_group
        )

        namespaces_list = [
            ('posts:index', []),
            ('posts:group_list', [new_group.slug]),
            ('posts:profile', [new_user.username]),
        ]

        for namespace, args in namespaces_list:
            with self.subTest(namespace=namespace):
                url = reverse(namespace, args=args)
                response = self.auth_client.get(url)
                page_obj = response.context['page_obj']
                self.assertIn(
                    new_post,
                    page_obj.paginator.object_list,
                    msg=f'View-функция {namespace} не отображает новый пост'
                )

    def test_view_exclude_new_post(self):
        """Test-function: view exclude new post."""
        new_user = User.objects.create_user(username='new_user')
        new_group = Group.objects.create(
            title='test new group',
            description='test new group description',
            slug='new_test_group'
        )
        new_post = Post.objects.create(
            text='Это текст поста примеси',
            author=new_user,
            group=new_group
        )

        namespaces_list = [
            ('posts:group_list', [PostsViewsTest.group.slug]),
            ('posts:profile', [PostsViewsTest.user.username]),
        ]

        for namespace, args in namespaces_list:
            with self.subTest(namespace=namespace):
                url = reverse(namespace, args=args)
                response = self.auth_client.get(url)
                page_obj = response.context['page_obj']
                self.assertNotIn(
                    new_post,
                    page_obj.paginator.object_list,
                    msg=(f'View-функция {namespace} отображает новый пост, '
                         f'принадлежащий другой выборке')
                )

    def test_invalid_views_args_return_404(self):
        """Test-function: invalid views args return 404 status."""
        namespaces_args = [
            ('posts:group_list', 'invalid_arg'),
            ('posts:profile', 'invalid_arg'),
            ('posts:post_detail', 404),
        ]

        for namespace, arg in namespaces_args:
            with self.subTest(namespace=namespace):
                url = reverse(namespace, args=[arg])
                response = self.auth_client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.NOT_FOUND,
                    (f'Для неверного параметра в {namespace} '
                     f'должны получить ошибку 404')
                )

    def test_index_cache(self):
        """
        Test-function: index page return cached content,
        until cache not clear.
        """
        response = self.auth_client.get(reverse('posts:index'))
        Post.objects.filter(
            pk=response.context['page_obj'][0].id
        ).delete()

        cache_response = self.auth_client.get(reverse('posts:index'))
        self.assertEqual(
            response.content,
            cache_response.content,
            msg='Главная страница не вернула закэшированный контент'
        )

        cache.clear()
        new_response = self.auth_client.get(reverse('posts:index'))
        self.assertNotEqual(
            response.content,
            new_response.content,
            msg=('После очистки кэша, главная страница вернула '
                 'закэшированный контент')
        )

    def test_user_cannot_follow_yourself(self):
        """Test-function: user can't follow yourself."""
        user = PostsViewsTest.user
        args = [user.username]
        url = reverse('posts:profile_follow', args=args)
        response = self.auth_client.get(url)
        self.assertRedirects(
            response,
            reverse('posts:profile', args=args)
        )
        self.assertFalse(
            user.follower.filter(following=user).exists(),
            msg='Пользователь не может подписываться на себя'
        )

    def test_user_can_follow(self):
        """Test-function: user can follow."""
        user = PostsViewsTest.user
        args = [PostsViewsTest.second_user.username]
        url = reverse('posts:profile_follow', args=args)
        response = self.auth_client.get(url)
        self.assertRedirects(
            response,
            reverse('posts:profile', args=args)
        )
        self.assertTrue(
            user.follower.filter(following=PostsViewsTest.second_user).exists(),
            msg='Не удалось подписаться на автора'
        )

    def test_user_can_unfollow(self):
        """Test-function: user can unfollow."""
        user = PostsViewsTest.user
        args = [PostsViewsTest.third_user.username]
        url = reverse('posts:profile_unfollow', args=args)
        response = self.auth_client.get(url)
        self.assertRedirects(
            response,
            reverse('posts:profile', args=args)
        )
        self.assertFalse(
            user.follower.filter(following=PostsViewsTest.third_user).exists(),
            msg='Не удалось отписаться от автора'
        )

    def test_follow_index(self):
        url = reverse('posts:follow_index')
        response = self.auth_client.get(url)
        self.assertFalse(
            response.context['page_obj'].paginator.count,
            ('Если авторы пользователя ничего не написали, '
             'page_obj должен быть пустым')
        )
        new_post = Post.objects.create(
            text='any text',
            author=PostsViewsTest.third_user
        )
        response = self.auth_client.get(url)
        self.assertIn(
            new_post,
            response.context['page_obj'].paginator.object_list,
            'Подписчик должен видеть новый пост автора в follow index'
        )
        second_user_client = Client()
        second_user_client.force_login(PostsViewsTest.second_user)
        response = second_user_client.get(url)
        self.assertFalse(
            response.context['page_obj'].paginator.count,
            'Если пользователь не имеет подписок page_obj должен быть пустым'
        )
        Follow.objects.create(
            user=PostsViewsTest.second_user,
            following=PostsViewsTest.user
        )
        response = second_user_client.get(url)
        self.assertNotIn(
            new_post,
            response.context['page_obj'].paginator.object_list,
            ('Подписчик не должен видеть в follow index посты авторов,'
             'на которых не подписан')
        )

    def test_correct_image_in_context(self):
        """Test-function: images in context is correct."""
        def check_image_path(image):
            if image:
                self.assertTrue(
                    os.path.exists(image.path),
                    f'не найден файл по пути {image.path}'
                )

        namespaces_list = [
            ('posts:index', [], True),
            ('posts:group_list', [PostsViewsTest.group.slug], True),
            ('posts:profile', [PostsViewsTest.user.username], True),
            ('posts:post_detail', [PostsViewsTest.post_image.id], False),
        ]
        for namespace, args, is_pagination in namespaces_list:
            url = reverse(namespace, args=args)
            response = self.auth_client.get(url)
            with self.subTest(url=url):
                if is_pagination:
                    page_obj = response.context['page_obj']
                    for post in page_obj.paginator.object_list:
                        check_image_path(post.image)
                else:
                    check_image_path(response.context['post'].image)
