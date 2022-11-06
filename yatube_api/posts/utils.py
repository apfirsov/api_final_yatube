"""
Posts app's utils functions.
"""
from django.core.paginator import Paginator, Page
from django.core.handlers.wsgi import WSGIRequest
from django.db.models.query import QuerySet
from .models import Post


def get_paginator_page_object(request: WSGIRequest,
                              object_list: QuerySet) -> Page:
    """Function creates Page-object using paginator and returns him."""
    count_page_posts = 10
    paginator = Paginator(object_list, count_page_posts)
    return paginator.get_page(request.GET.get('page'))


def get_posts_list(*args, **kwargs) -> QuerySet:
    """Function returns posts list from Post-model with related objects."""
    queryset = (
        Post.objects.select_related('group', 'author')
            .filter(*args, **kwargs).order_by('-pub_date')
    )
    return queryset.all()
