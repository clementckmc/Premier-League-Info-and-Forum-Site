from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import fields
from django.forms import ModelForm, widgets
from django import forms
from django.urls import reverse
from django.db.models import Max

# Create your models here.
class User(AbstractUser):
    pass

PL_CLUBS = [
    ("ARS", "Arsenal"),
    ("AST", "Aston Villa"),
    ("CHE", "Chelsea"),
    ("EVE", "Everton"),
    ("LIV", "Liverpool"),
    ("MCI", "Man City"),
    ("MUN", "Man United"),
    ("NEW", "Newcastle"),
    ("NOR", "Norwich"),
    ("TOT", "Tottenham"),
    ("WOL", "Wolverhampton"),
    ("BUR", "Burnley"),
    ("LEI", "Leicester City"),
    ("SOU", "Southampton"),
    ("LEE", "Leeds United"),
    ("WAT", "Watford"),
    ("CRY", "Crystal Palace"),
    ("BHA", "Brighton Hove"),
    ("BRE", "Brentford"),
    ("WHU", "West Ham"),
    ("GEN", "general")
]

class Thread(models.Model):
    op = models.ForeignKey('football.User', on_delete=models.CASCADE, related_name='op_thread')
    topic = models.CharField(max_length=50, blank=False)
    content = models.TextField(max_length=500)
    forum = models.CharField(choices=PL_CLUBS, max_length=20)
    time = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True)
    upvote = models.ManyToManyField(User, related_name="thread_upvote", blank=True)
    downvote = models.ManyToManyField(User, related_name="thread_downvote", blank=True)

    def get_reply_count(self):
        return Reply.objects.filter(thread=self).count()

    def get_url(self):
        return reverse('thread', kwargs={'slug': self.slug})

    @property
    def get_upvote(self):
        return Thread.upvote.through.objects.filter(thread_id=self.id).count()

    @property
    def get_downvote(self):
        return Thread.downvote.through.objects.filter(thread_id=self.id).count()

class ThreadForm(ModelForm):
    class Meta:
        model = Thread
        fields = ['topic', 'content']
        labels = {
            'topic': 'Topic: '
        }
        widgets = {
            'content': widgets.Textarea(attrs={'cols':120, 'rows': 10})
        }

class Reply(models.Model):
    poster = models.ForeignKey('football.User', on_delete=models.CASCADE, related_name='user_reply')
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='reply')
    content = models.TextField(max_length=500)
    time = models.DateTimeField(auto_now_add=True)
    upvote = models.ManyToManyField(User, related_name="reply_upvote", blank=True)
    downvote = models.ManyToManyField(User, related_name="reply_downvote", blank=True)

    @property
    def get_upvote(self):
        return Reply.upvote.through.objects.filter(reply_id=self.id).count()

    @property
    def get_downvote(self):
        return Reply.downvote.through.objects.filter(reply_id=self.id).count()

class ReplyForm(ModelForm):
    class Meta:
        model = Reply
        fields = ['content']
        widgets = {
            'content': widgets.Textarea(attrs={'cols':120, 'rows': 10, 'class': 'replyBox'})
        }