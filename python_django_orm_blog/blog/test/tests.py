import django.db  # noqa: F401
import pytest

from python_django_orm_blog.blog import models


@pytest.mark.django_db
def test_clip_rates_for():
    new_one = models.Clip.objects.create(title='The lazy cat')
    assert models.Clip.rates_for(id=new_one.id) == (0, 0)

    jokes = models.Clip.objects.create(title='Stupid jokes')
    for _ in range(7):
        jokes.dislike()
    for _ in range(10):
        jokes.like()
    assert models.Clip.rates_for(title=jokes.title) == (10, 7)
