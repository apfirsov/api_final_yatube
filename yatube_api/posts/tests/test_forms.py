import shutil
import tempfile
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from ..models import Post, Group, User, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTest(TestCase):
    """Posts app forms test-class."""

    @classmethod
    def setUpClass(cls):
        """Makes class-fixtures for tests of posts app forms."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='test group 1',
            description='test group 1 description',
            slug='first_test_group'
        )
        cls.post = Post.objects.create(
            text='Это текст первого тестового поста',
            author=cls.user,
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def check_post_form_fields(cls, test_obj, form):
        """cheking form fields."""
        fields_check_list = [
            ('text', 'Текст поста', 'Текст нового поста'),
            ('group', 'Группа', 'Группа, к которой будет относиться пост')
        ]
        for name, label, help_text in fields_check_list:
            test_obj.assertIn(
                name,
                form.fields,
                f'в форме поста не найдено поле "{name}"')
            test_obj.assertEqual(
                form.fields[name].label,
                label,
                f'в форме поста не верный label в поле "{name}"')
            test_obj.assertEqual(
                form.fields[name].help_text,
                help_text,
                f'в форме поста не верный help_text в поле "{name}"')

    @classmethod
    def get_uploaded_image(cls, image_name):
        """Generate test image, used SimpleUploadedFile."""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        return SimpleUploadedFile(
            name=image_name,
            content=small_gif,
            content_type='image/gif'
        )

    def setUp(self) -> None:
        """Set test settings."""
        cache.clear()
        self.client = Client()
        self.auth_client = Client()
        self.auth_client.force_login(PostsFormsTest.user)

    def test_guest_can_not_posting_forms(self):
        """
        Test-function: guest can't create, edit or add comments to a post.
        """
        login_url = reverse('users:login')
        namespaces_list = [
            ('posts:post_create', {}),
            ('posts:post_edit', {'post_id': PostsFormsTest.post.id}),
            ('posts:add_comment', {'post_id': PostsFormsTest.post.id}),
        ]

        posts_count = Post.objects.count()
        comments_count = Comment.objects.count()
        new_text = 'any text'

        for namespace, kwargs in namespaces_list:
            url = reverse(namespace, kwargs=kwargs)
            with self.subTest(url=url):
                response = self.client.post(
                    url,
                    data={'text': new_text},
                    follow=True
                )
                self.assertRedirects(
                    response,
                    f'{login_url}?next={url}',
                    msg_prefix=(f'Гость должен направляться на авторизацию'
                                f' при попытке post-запроса к {url}')
                )
                self.assertEqual(
                    Post.objects.count(),
                    posts_count,
                    (f'Количество постов в БД изменилось после '
                     f'действий гостя {url}')
                )
                self.assertEqual(
                    Comment.objects.count(),
                    comments_count,
                    (f'Количество комментариев в БД изменилось после '
                     f'действий гостя {url}')
                )
                if len(kwargs):
                    post_db = Post.objects.get(pk=kwargs['post_id'])
                    self.assertNotEqual(
                        post_db.text,
                        new_text,
                        f'Текст поста {kwargs} изменился после действий гостя'
                    )

    def test_form_create_new_post_auth_user(self):
        """Test-function: create new post."""
        url = reverse('posts:post_create')
        posts_count = Post.objects.count()
        new_post_text = 'Пост из формы создания нового'
        form_data = {
            'text': new_post_text,
            'group': PostsFormsTest.group.id
        }
        response = self.auth_client.post(
            url,
            data=form_data,
            follow=True
        )
        with self.subTest(url=url):
            self.assertEqual(
                Post.objects.count(),
                posts_count + 1,
                (f'Количество постов в БД не изменилось после '
                 f'создания в форме {url}')
            )
            new_post_exist = Post.objects.filter(
                text=new_post_text,
                group=PostsFormsTest.group.id
            ).exists()
            self.assertTrue(new_post_exist, 'Созданный пост не найден')
            self.assertRedirects(
                response,
                reverse('posts:profile', args=[PostsFormsTest.user.username]),
                msg_prefix=('После создания поста пользователь должен '
                            'перенаправлятся на свою страницу')
            )

    def test_form_edit_post_auth_user(self):
        """Test-function: edit post."""
        posts_count = Post.objects.count()
        url = reverse('posts:post_edit', args=[PostsFormsTest.post.id])
        new_text = 'Новый текст поста'
        new_group = Group.objects.create(
            title='новая группа',
            description='новая группа',
            slug='new_group'
        )
        form_data = {
            'text': new_text,
            'group': new_group.id
        }
        response = self.auth_client.post(
            url,
            data=form_data,
            follow=True
        )
        with self.subTest(url=url):
            post = Post.objects.get(pk=PostsFormsTest.post.id)
            self.assertEqual(post.text, new_text)
            self.assertEqual(post.group, new_group)
            self.assertEqual(
                Post.objects.count(),
                posts_count,
                (f'Количество постов в БД изменилось после '
                 f'редактирования в форме {url}')
            )
            self.assertRedirects(
                response,
                reverse('posts:post_detail', args=[PostsFormsTest.post.id]),
                msg_prefix=('После редактирования поста пользователь должен '
                            'перенаправлятся на страницу этого поста')
            )

    def test_form_add_comment_auth_user(self):
        """Test-function: add comment."""
        pk_args = [PostsFormsTest.post.id]
        url = reverse('posts:add_comment', args=pk_args)
        post_url = reverse('posts:post_detail', args=pk_args)
        query_set = Comment.objects.filter(post=PostsFormsTest.post)
        comments_count = query_set.count()

        new_comment_text = 'Новый комментраий'
        form_data = {
            'text': new_comment_text,
        }
        response = self.auth_client.post(
            url,
            data=form_data,
            follow=True
        )
        with self.subTest(url=url):
            self.assertEqual(
                query_set.count(),
                comments_count + 1,
                (f'Количество комментариев к посту в БД не изменилось после '
                 f'добавления в {url}')
            )
            query_set = query_set.filter(text=new_comment_text)

            self.assertTrue(query_set.exists(), 'Новый комментарий не найден')
            self.assertRedirects(
                response,
                post_url,
                msg_prefix=('После добавления комментария пользователь '
                            'должен перенаправлятся на страницу поста')
            )
            comment = query_set.get()
            post_response = self.auth_client.get(post_url)
            self.assertIn(
                comment,
                post_response.context['page_obj'].paginator.object_list,
                msg='Новый комментраий не появился на странице поста'
            )

    def test_create_form_in_context(self):
        """Test-function: checking form instance and fields in create form."""
        url = reverse('posts:post_create')
        response = self.auth_client.get(url)
        with self.subTest(url=url):
            form = response.context['form']
            self.assertIsNone(
                form.instance.id,
                'Форма создания поста должна содержать новый пустой объект'
            )
            PostsFormsTest.check_post_form_fields(self, form)

    def test_edit_form_in_context(self):
        """Test-function: checking form instance and fields in edit form."""
        url = reverse('posts:post_edit', args=[PostsFormsTest.post.id])
        response = self.auth_client.get(url)
        with self.subTest(url=url):
            form = response.context['form']
            self.assertEqual(
                form.instance,
                PostsFormsTest.post,
                ('Форма редактрования поста должна содержать '
                 'редактируемый объект')
            )
            PostsFormsTest.check_post_form_fields(self, form)

    def test_image_upload_in_create_form(self):
        """Test-function: image correct upload in create form."""
        image_name = 'create_small.gif'
        form_data = {
            'text': image_name,
            'group': PostsFormsTest.group.id,
            'image': PostsFormsTest.get_uploaded_image(image_name)
        }
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=[PostsFormsTest.user.username]),
        )

        post = Post.objects.filter(
            text=image_name,
            group=PostsFormsTest.group,
        ).get()

        image_name = f'posts/{image_name}'
        self.assertEqual(
            post.image.name,
            image_name,
            msg='Не удалось создать пост с изображением'
        )

    def test_image_upload_in_edit_form(self):
        """Test-function: image correct upload in edit form."""
        image_name = 'edit_small.gif'
        form_data = {
            'text': PostsFormsTest.post.text,
            'image': PostsFormsTest.get_uploaded_image(image_name)
        }
        response = self.auth_client.post(
            reverse('posts:post_edit', args=[PostsFormsTest.post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=[PostsFormsTest.post.id]),
        )

        post = Post.objects.get(pk=PostsFormsTest.post.id)
        image_name = f'posts/{image_name}'
        self.assertEqual(
            post.image.name,
            image_name,
            msg='Не удалось загрузить изображение при редактировании поста'
        )
