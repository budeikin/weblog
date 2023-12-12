from django.http import Http404
from django.shortcuts import render, get_object_or_404
from .models import Post


# Create your views here.

def post_list(request):
    all_posts = Post.published.all()
    context = {
        'posts': all_posts
    }
    return render(request, 'blog/post/post_list.html', context)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, publish__year=year, publish__month=month, publish__day=day, slug=post,
                             status=Post.Status.PUBLISHED)
    context = {'post': post}
    return render(request, 'blog/post/post_detail.html', context)
