from django.contrib import admin
from forum.models import Topic, Post, Vote, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date_created', 'display_topic')
    list_filter = ('is_approved', 'author')


admin.site.register(Topic)
admin.site.register(Vote)
admin.site.register(Comment)
