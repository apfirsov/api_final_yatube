from django.contrib import admin
from .models import Post, Group, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    """Admin class for model class Post."""

    list_display = ('pk', 'text', 'pub_date', 'author', 'group',)
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """Admin class for model class Group."""

    list_display = ('pk', 'title', 'slug',)
    search_fields = ('title',)


class CommentAdmin(admin.ModelAdmin):
    """Admin class for model class Comment."""

    list_display = ('pk', 'post', 'author', 'text', 'created',)
    search_fields = ('text',)
    list_filter = ('post', 'author', 'created',)


class FollowAdmin(admin.ModelAdmin):
    """Admin class for model class Follow."""

    list_display = ('pk', 'user', 'following',)
    list_filter = ('user', 'following',)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
