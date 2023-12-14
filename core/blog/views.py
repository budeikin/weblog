from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.views.generic import ListView, DetailView
from .forms import EmailPostForm, CommentForm
from django.core.mail import send_mail
from django.views.decorators.http import require_POST


# Create your views here.
class PostListView(ListView):
    queryset = Post.published.all()
    paginate_by = 3
    context_object_name = 'posts'
    template_name = 'blog/post/post_list.html'


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
