from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.views.generic import ListView, DetailView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.db.models import Count
from taggit.models import Tag


# Create your views here.
# class PostListView(ListView):
#     paginate_by = 3
#     context_object_name = 'posts'
#     template_name = 'blog/post/post_list.html'
#
#     def get_queryset(self, tag_slug=None):
#         if self.kwargs['tag_slug']:
#             tag = get_object_or_404(Tag, slug=tag_slug)
#             queryset = super().get_queryset().filter(tags__in=[tag])
#         else:
#             queryset = Post.published.all()
#         return queryset


def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    # Pagination with 3 posts per page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:

        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'blog/post/post_list.html',
                  {'posts': posts,
                   'tag': tag})


# def post_list(request):
#     post_list = Post.published.all()
#     paginator = Paginator(post_list, 3)
#     page_number = request.GET.get('page', 1)
#     try:
#         posts = paginator.page(page_number)
#     except EmptyPage:
#         posts = paginator.page(paginator.num_pages)
#     except PageNotAnInteger:
#         posts = paginator.page(1)
#     return render(request, 'blog/post/post_list.html', {'posts': posts})


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post/post_detail.html'

    def get_object(self):
        post = get_object_or_404(Post, publish__year=self.kwargs['year'], publish__month=self.kwargs['month'],
                                 publish__day=self.kwargs['day'], slug=self.kwargs['post'],
                                 status=Post.Status.PUBLISHED)

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['comments'] = self.get_object().comments.filter(active=True)
        context['form'] = CommentForm()
        post_tags_ids = self.object.tags.values_list('id', flat=True)
        similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=self.object.id)
        similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
        context['similar_posts'] = similar_posts
        return context


# def post_detail(request, year, month, day, post):
#     post = get_object_or_404(Post, publish__year=year, publish__month=month, publish__day=day, slug=post,
#                              status=Post.Status.PUBLISHED)
#     context = {'post': post}
#     return render(request, 'blog/post/post_detail.html', context)
#


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read " \
                      f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'budeikin52@gmail.com', [cd['to'], ])

            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    return render(request, 'blog/post/comment.html', {'form': form, 'post': post, 'comment': comment})
