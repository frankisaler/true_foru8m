from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import generic
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from .forms import PostForm
from forum.models import Post, Topic, Vote
from authentication.models import User

import datetime


def create_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)

    try:
        comment_text = request.POST['comment_text']
    except KeyError as key_err:
        return handle_error(request, post, str(key_err))

    if comment_text != "":
        post.comment_set.create(text=comment_text, post=post, author=request.user)
        return HttpResponseRedirect(reverse('post-detail', args=(post.id,)))
    else:
        return handle_error(request, post, "Вы должны написать что-то!")


def handle_error(request, post, err_msg):
    return render(request, 'forum/post_detail.html', {
        'post': post,
        'error_msg': err_msg
    })


def index(request):
    context = {
        'topics': get_top_topics(),
    }
    return render(request, 'forum/index.html', context=context)


def get_top_topics():
    """Returns top 3 topics based on number of posts in a topic."""
    topics = []
    all_topics = Topic.objects.all()
    for topic in all_topics:
        topics.append({'topic_name': topic.name, 'occurrence': Post.objects.filter(topic=topic.id).count()})
    topics.sort(key=lambda x: x['occurrence'],reverse=True)
    return topics[:3]


def get_profile(request, pk):
    profile = get_object_or_404(User, username = pk)
    post_count = Post.objects.filter(author=profile.pk).count()
    return render(request, 'forum/profile.html', {'get_profile': profile, 'post_count': post_count})


@login_required
def voting(request, pk, vote):

    if request.method == "POST":
        post = get_object_or_404(Post, id=pk)

        try:
            obj = Vote.objects.get(user=request.user, post=post)

            if obj.value != vote:

                if vote == 1 and obj.value == 2:
                    post.votes_up += 1
                    post.votes_down -= 1
                elif vote == 2 and obj.value == 1:
                    post.votes_up -= 1
                    post.votes_down += 1

                obj.value = vote
                obj.save()
                post.save()

            return HttpResponseRedirect(reverse('post-detail', args=(pk,)))
        except Vote.DoesNotExist:
            vote_new = Vote()
            vote_new.user = request.user
            vote_new.post = post
            vote_new.value = vote

            if vote == 1:
                post.votes_up += 1
            elif vote == 2:
                post.votes_down += 1

            vote_new.save()
            post.save()

            return HttpResponseRedirect(reverse('post-detail', args=(post.id,)))
    else:
        post = get_object_or_404(Post, id=pk)
        return HttpResponseRedirect(reverse('post-detail', args=(post.id,)))


class PostListView(generic.ListView):
    model = Post
    paginate_by = 5
    template_name = 'forum/post_list.html'

    def get_queryset(self):
        return Post.objects.order_by('-votes_up')


class PostDetailView(generic.DetailView):
    model = Post


class PostsByTopic(generic.ListView):
    model = Post
    template_name = 'forum/post_list.html'
    paginate_by = 5

    def get_queryset(self):
        return Post.objects.filter(topic=self.request.pk).order_by('date_created')


class PostsByUser(LoginRequiredMixin, generic.ListView):
    model = Post
    template_name = 'forum/post_list.html'
    paginate_by = 5

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).order_by('date_created')


class PostCreate(LoginRequiredMixin, generic.CreateView):
    form_class = PostForm
    template_name = 'forum/post_create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super(PostCreate, self).form_valid(form)


class PostUpdate(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Post
    template_name = 'forum/post_create.html'
    fields = ['title', 'body', 'topic']

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class PostDelete(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Post
    success_url = reverse_lazy('my-posts')
    template_name = 'forum/post_confirm_delete.html'

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class SearchResult(generic.ListView):
    model = Post
    template_name = 'forum/post_list.html'

    def get_queryset(self):
        query = self.request.GET.get("q")
        time = self.request.GET.get("t")

        if time == '1':  # all time
            if '#' in query:
                return Post.objects.filter(Q(topic__name=query[1:]), date_created__lte=datetime.datetime.today())
            return Post.objects.filter(
                Q(title__icontains=query) | Q(body__icontains=query), date_created__lte=datetime.datetime.today()
            )
        if time == '2':  # today
            today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
            today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
            if '#' in query:
                return Post.objects.filter(Q(topic__name=query[1:]), date_created__range=(today_min, today_max))
            return Post.objects.filter(
                Q(title__icontains=query) | Q(body__icontains=query), date_created__range=(today_min, today_max)
            )
        if time == '3':  # a month ago
            today = datetime.datetime.today()
            if today.month == 1:
                today = today.replace(month=12, year=today.year - 1)
            else:
                today = today.replace(month=today.month - 1)
            if '#' in query:
                return Post.objects.filter(Q(topic__name=query[1:]), date_created__gte=today)
            return Post.objects.filter(
                Q(title__icontains=query) | Q(body__icontains=query), date_created__gte=today
            )


class PostsByTopic(generic.ListView):
    model = Post
    template_name = 'forum/post_list.html'

    def get_queryset(self):
        topic = self.request.GET.get("topic")
        return Post.objects.filter(topic__name=self.kwargs['topic'])


class PostAfterComment(generic.DetailView):
    model = Post
    template_name = "forum/post_detail.html"
