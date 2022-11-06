from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, Http404, redirect
from .forms import PostForm, CommentForm
from .models import Post, Group, User
from . import utils


def index(request: WSGIRequest):
    """Index page view-function."""
    posts = utils.get_posts_list()
    template = 'posts/index.html'
    context = {
        'page_obj': utils.get_paginator_page_object(request, posts)
    }
    return render(request, template, context)


def group_posts(request: WSGIRequest, slug: str):
    """Group page view-function."""
    group = get_object_or_404(Group, slug=slug)
    posts = utils.get_posts_list(group=group)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': utils.get_paginator_page_object(request, posts)
    }
    return render(request, template, context)


def profile(request: WSGIRequest, username: str):
    """Profile page view-function."""
    author = get_object_or_404(User, username=username)
    posts = utils.get_posts_list(author=author)
    following = (request.user.is_authenticated
                 and author.following.filter(user=request.user).exists())
    template = 'posts/profile.html'
    context = {
        'author': author,
        'following': following,
        'page_obj': utils.get_paginator_page_object(request, posts)
    }
    return render(request, template, context)


def post_detail(request: WSGIRequest, post_id: int):
    """Post detail page view-function."""
    post = (Post.objects.select_related('group', 'author').filter(pk=post_id)
            .annotate(author_posts_count=Count('author__posts')).first())

    if post is None:
        raise Http404(f'По коду {post_id} пост не найден!')

    comments = post.comments.select_related('author').all()
    comments_page_obj = utils.get_paginator_page_object(request, comments)

    template = 'posts/post_detail.html'
    context = {
        'post': post,
        'comment_form': CommentForm(),
        'page_obj': comments_page_obj
    }
    return render(request, template, context)


@login_required
def post_create(request: WSGIRequest):
    """Post creation page view-function."""
    form = PostForm(
        data=request.POST or None,
        files=request.FILES or None
    )

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)

    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': False
    }
    return render(request, template, context)


@login_required
def post_edit(request: WSGIRequest, post_id: int):
    """Post editing page view-function."""
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        data=request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': True
    }

    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Comment adding view-function."""
    post = get_object_or_404(Post, pk=post_id)

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Follow index page view-function."""
    template = 'posts/follow.html'
    posts = utils.get_posts_list(author__following__user=request.user)
    context = {
        'page_obj': utils.get_paginator_page_object(request, posts)
    }

    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        author.following.get_or_create(user=request.user)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    author.following.filter(user=request.user).delete()
    return redirect('posts:profile', username=username)
