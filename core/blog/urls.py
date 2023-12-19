from django.urls import path
from .views import post_list, PostDetailView, post_share, post_comment
from .feeds import LatestPostsFeed

app_name = 'blog'

urlpatterns = [
    path('', post_list, name='post_list'),
    path('tag/<slug:tag_slug>/', post_list, name='post_list_by_tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', PostDetailView.as_view(), name='post_detail'),
    path('<int:post_id>/share/', post_share, name='post_share'),
    path('<int:post_id>/comment/', post_comment, name='post_comment'),
    path('feed/', LatestPostsFeed(), name='post_feed'),
]
