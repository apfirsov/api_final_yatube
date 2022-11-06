from django.core.cache import cache
from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse
from ..models import Post, Group, User


class PostsURLTest(TestCase):
    """Posts app URL test-class."""

    @classmethod
    def setUpClass(cls):
        """Makes class-fixtures for tests of posts app URLs."""
        super().setUpClass()
        cls.another_user = User.objects.create_user(username='test_another')
        cls.author = User.objects.create_user(username='test_author')
        cls.group = Group.objects.create(
            title='test group 1',
            description='test group 1 description',
            slug='first_test_group'
        )
        cls.post = Post.objects.create(
            text='Это текст первого тестового поста',
            author=cls.author,
            group=cls.group
        )

    @classmethod
    def check_common_urls(cls, test_obj):
        """Checking common URLs templates with different settings."""
        common_urls = [
            ('/', 'posts/index.html'),
            (f'/group/{cls.group.slug}/', 'posts/group_list.html'),
            (f'/profile/{cls.author.username}/', 'posts/profile.html'),
            (f'/posts/{cls.post.id}/', 'posts/post_detail.html'),
        ]
        for url, template in common_urls:
            with test_obj.subTest(url=url, template=template):
                response = test_obj.client.get(url)
                is_authenticated = response.wsgi_request.user.is_authenticated
                test_obj.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    (f'Страница {url} должна быть доступна '
                     f'{"пользователю" if is_authenticated else "гостю"}')
                )
                test_obj.assertTemplateUsed(
                    response,
                    template,
                    f'Страница {url} не использует шаблон {template}'
                )

    def setUp(self):
        """Set test settings."""
        cache.clear()
        self.client = Client()

    def test_unexisting_url_return_404_status(self):
        """Test-function: unexisting URL return 404 status."""
        url = '/unexisting_page/'
        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
            'Запрос к несуществующей странице должен возвращать ошибку 404'
        )

    def test_urls_guest(self):
        """Test-function: URL uses correct template for guest."""
        PostsURLTest.check_common_urls(self)

        login_url = reverse('users:login')
        auth_urls = [
            f'/posts/{PostsURLTest.post.id}/edit/',
            '/create/',
            '/follow/',
            f'/profile/{PostsURLTest.author.username}/follow/',
            f'/profile/{PostsURLTest.author.username}/unfollow/',
            f'/posts/{PostsURLTest.post.id}/comment/',
        ]

        for url in auth_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    f'{login_url}?next={url}',
                    msg_prefix=('Гость должен направляться на '
                                'страницу авторизации')
                )

    def test_urls_use_correct_template_auth_client(self):
        """Test-function: URL uses correct template for authorized client."""
        self.client.force_login(PostsURLTest.author)
        PostsURLTest.check_common_urls(self)

        auth_urls = [
            ('/create/', 'posts/create_post.html'),
            ('/follow/', 'posts/follow.html'),
            (
                f'/posts/{PostsURLTest.post.id}/edit/',
                'posts/create_post.html'
            ),
        ]
        for url, template in auth_urls:
            with self.subTest(url=url, template=template):
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    (f'Страница {url} должна быть доступна '
                     f'зарегистрированному пользователю')
                )
                self.assertTemplateUsed(
                    response,
                    template,
                    f'Страница {url} не использует шаблон {template}'
                )

    def test_urls_use_correct_redirect_auth_client(self):
        """Test-function: URL uses correct redirect for authorized client."""
        self.client.force_login(PostsURLTest.another_user)

        redir_urls = [
            (
                f'/posts/{PostsURLTest.post.id}/comment/',
                'posts:post_detail', [PostsURLTest.post.id],
            ),
            (
                f'/profile/{PostsURLTest.author.username}/follow/',
                'posts:profile', [PostsURLTest.author.username],
            ),
            (
                f'/profile/{PostsURLTest.author.username}/unfollow/',
                'posts:profile', [PostsURLTest.author.username],
            ),
        ]
        for url, redir_name, redir_agrs in redir_urls:
            redir_url = reverse(redir_name, args=redir_agrs)
            with self.subTest(url=url, redir_url=redir_url):
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    redir_url,
                    msg_prefix='редирект работает не правильно'
                )

    def test_another_user_can_not_edit_post(self):
        """Test-function: Another user can not edit post."""
        self.client.force_login(PostsURLTest.another_user)
        url = f'/posts/{PostsURLTest.post.id}/edit/'
        expected = reverse('posts:post_detail', args=[PostsURLTest.post.id])
        response = self.client.get(url)
        self.assertRedirects(response, expected)
