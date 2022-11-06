from django.test import TestCase
from ..models import Post, Group, User, POST_STR_LENGTH


class PostsModelsTest(TestCase):
    """Posts app models test-class."""

    @classmethod
    def setUpClass(cls):
        """Makes class-fixtures for tests."""
        super().setUpClass()

        cls.group = Group.objects.create(
            title='тестовая группа №1',
            description='Это тестовая группа №1',
            slug='test_one'
        )

        cls.post = Post.objects.create(
            text='Это текст первого тестового поста',
            author=User.objects.create_user(username='test_user'),
            group=cls.group
        )

    def test_str_method(self):
        """Test-function: models magic method __str__"""
        object_list = [
            (
                PostsModelsTest.post,
                PostsModelsTest.post.text[:POST_STR_LENGTH],
                'первые 15 симолов поля text'
            ),
            (
                PostsModelsTest.group,
                PostsModelsTest.group.title,
                'значение поля title'
            ),
        ]

        for obj, expection_value, expection_name in object_list:
            with self.subTest(obj=obj, expection_value=expection_value):
                self.assertEqual(
                    str(obj),
                    expection_value,
                    (f'Проверьте, что метод __str__ класса '
                     f'{type(obj).__name__} возвращает {expection_name}')
                )
