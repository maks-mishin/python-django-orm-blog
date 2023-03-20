import pytest
from python_django_orm_blog.blog import models


@pytest.mark.django_db
def test_creation():
    vote1 = models.Vote.in_favour('test')
    assert isinstance(vote1, models.Vote)
    assert vote1.positive

    vote2 = models.Vote.against('test')
    assert isinstance(vote2, models.Vote)
    assert not vote2.positive

    assert models.Vote.objects.count() == 2


@pytest.mark.django_db
def test_count():
    plan = 'Make some stupid'
    for _ in range(5):
        models.Vote.in_favour(plan)
    for _ in range(7):
        models.Vote.against(plan)
    assert models.Vote.objects.filter(positive=True).count() == 5
    assert models.Vote.objects.filter(positive=False).count() == 7
