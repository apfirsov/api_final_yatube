from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()
POST_STR_LENGTH: int = 15


class Group(models.Model):
    """Group model class."""

    title = models.CharField('Имя', max_length=200)
    slug = models.SlugField(
        'Адрес', max_length=50, db_index=True, unique=True
    )
    description: str = models.TextField('Описание')

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    def __str__(self):
        return self.title


class Post(models.Model):
    """Post model class."""

    text = models.TextField('Текст')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    group = models.ForeignKey(
        Group,
        verbose_name='Сообщество',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор')
    image = models.ImageField(
        'Картинка', upload_to='posts/', null=True, blank=True)

    class Meta:
        # ordering = ['-pub_date']
        default_related_name = 'posts'
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:POST_STR_LENGTH]


class Comment(models.Model):
    """Comment model class."""

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор')
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, verbose_name='Пост')
    text = models.TextField('Текст')
    created = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created']
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'{self.author} - {self.text[:POST_STR_LENGTH]}'


class Follow(models.Model):
    """Follow model class."""

    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        related_name='follower',
        on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='following',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                name='unique_user_following',
                fields=('user', 'following'),
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='user_is_not_following'
            )
        ]
