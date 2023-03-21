from typing import Tuple

from django.db import models
from django.db.models import Count, Sum


class TimestampedModel(models.Model):
    """An abstract model with a pair of timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(TimestampedModel):
    """A blog user."""

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    nickname = models.CharField(max_length=100, null=True)


class Tag(TimestampedModel):
    """A tag for the group of posts."""

    title = models.CharField(max_length=100)


class Post(TimestampedModel):
    """A blog post."""

    title = models.CharField(max_length=200)
    body = models.TextField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag)


class PostComment(TimestampedModel):
    """A commentary to the blog post."""

    body = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    response_to = models.ForeignKey(
        'PostComment', on_delete=models.SET_NULL, null=True,
    )
    creator = models.ForeignKey(User, on_delete=models.CASCADE)


class PostLike(TimestampedModel):
    """A positive reaction to the blog post."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['post', 'creator']


class Vote(models.Model):
    subject = models.CharField(max_length=200)
    positive = models.BooleanField(default=True)

    @classmethod
    def in_favour(cls, subject):
        """Create a new vote in favour of the subject."""
        return cls.objects.create(subject=subject)

    @classmethod
    def against(cls, subject):
        """Create a new vote against of the subject."""
        return cls.objects.create(subject=subject, positive=False)

    @classmethod
    def results_for(cls, subject):
        """Return the voting results for the subject"""
        list_votes = cls.objects.filter(subject=subject)
        return {
            'in favour': list_votes.filter(positive=True).count(),
            'against': list_votes.filter(positive=False).count()
        }


class CycleInGraphError(Exception):
    """An exception that means that some graph has cycles."""
    pass


class Task(models.Model):
    value = models.CharField(max_length=200)
    parent = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.CASCADE
    )

    @property
    def root(self):
        """Returns a root task (task which parent is None)"""

        def search_root(task, task_set):
            if task.value in task_set:
                raise CycleInGraphError(task.id)
            if task.parent is None:
                return task
            task_set.add(task.value)
            return search_root(task.parent, task_set)

        root_task = search_root(self, set())
        return root_task


class Island(models.Model):
    name = models.CharField(max_length=200)

    def can_reach(self, island, *, by_ship):
        """Return True if one can reach the @island using a @by ship"""
        return by_ship in island.ships.all() and by_ship in self.ships.all()


class Ship(models.Model):
    name = models.CharField(max_length=200)
    islands = models.ManyToManyField(Island, related_name='ships')


class Clip(models.Model):
    title = models.CharField(max_length=200)

    def like(self):
        ClipLike.objects.create(clip=self)

    def dislike(self):
        ClipDislike.objects.create(clip=self)

    @classmethod
    def rates_for(cls, **kwargs) -> (int, int):
        """
        Returns a tuple of integers (likes, dislikes)
        for the clip(s) filtered by provided kwargs.
        """
        clip_likes = Clip.objects.filter(
            **kwargs
        ).annotate(
            count=Count('cliplike', dictinct=True)
        )[0]
        clip_dislikes = Clip.objects.filter(
            **kwargs
        ).annotate(
            count=Count('clipdislike', dictinct=True)
        )[0]
        return (
            clip_likes.count,
            clip_dislikes.count
        )


class ClipLike(models.Model):
    clip = models.ForeignKey(Clip, on_delete=models.CASCADE)


class ClipDislike(models.Model):
    clip = models.ForeignKey(Clip, on_delete=models.CASCADE)
