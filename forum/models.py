from django.db import models
from django.urls import reverse
from authentication.models import User
import datetime


class Topic(models.Model):
    name = models.CharField(max_length=50, help_text="Название темы.")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Post(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField(max_length=1000)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    # ForeignKey because a post can only have one author, but authors can have multiple posts.
    topic = models.ManyToManyField(Topic, help_text="Выберите тему для этого поста.")
    # ManyToManyField used because a topic can contain many posts and a post can cover many topics.
    is_approved = models.BooleanField(default=False)
    votes_up = models.IntegerField(default=0, blank=True)
    votes_down = models.IntegerField(default=0, blank=True)

    def __str__(self):
        return "{} спросил {}".format(self.author.username, self.title)

    def get_absolute_url(self):
        """Returns the url to access a particular post instance."""
        return reverse('post-detail', args=[str(self.id)])

    def display_topic(self):
        return '  '.join('#' + topic.name for topic in self.topic.all())

    def topics_to_list(self):
        return [topic for topic in self.topic.all()]

    display_topic.short_description = 'Topic'


class Comment(models.Model):
    text = models.TextField(max_length=500, help_text="Напишите свой комментарий")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        max_len = 100
        return self.text if len(self.text) < max_len else self.text[:max_len]+'...'

    def get_time(self):
        def time_calculator(time):
            if time < 60:
                return time, 'm'
            if time // 60 < 24:
                return time // 60, 'h'
            else:
                return time // 60 // 24, 'd'

        time_passed = datetime.datetime.astimezone(datetime.datetime.now()) - self.date_created
        time, unit_of_time = time_calculator(round(time_passed.total_seconds()/60))
        return "{} {} тому назад".format(time, unit_of_time)

    class Meta:
        order_with_respect_to = 'post'


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.IntegerField()

    def __str__(self):
        return "{} {} post: {}".format(self.user.username, "liked" if self.value == 1 else "disliked", self.post.title)

    class Meta:
        unique_together = ("user", "post", "value")
