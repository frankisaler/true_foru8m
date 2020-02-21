from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]

urlpatterns += [
    path('posts/', views.PostListView.as_view(), name='posts'),
    path('posts/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('posts/my-posts/', views.PostsByUser.as_view(), name='my-posts'),
]

urlpatterns += [
    path('posts/create/', views.PostCreate.as_view(), name='post-create'),
    path('posts/<int:pk>/delete/', views.PostDelete.as_view(), name='post-delete'),
    path('posts/<int:pk>/update/', views.PostUpdate.as_view(), name='post-update'),
]

urlpatterns += [
    path('search/', views.SearchResult.as_view(), name='search_results'),
    path('topics/<str:topic>/', views.PostsByTopic.as_view(), name='posts-topic'),
]

urlpatterns += [
    path('posts/<int:pk>/vote/<int:vote>/', views.voting, name='vote')
]

urlpatterns += [
    path('user/<str:pk>/', views.get_profile, name='user-detail'),
]

urlpatterns += [
    path('posts/<int:pk>/comment/', views.create_comment, name='comment'),
]
