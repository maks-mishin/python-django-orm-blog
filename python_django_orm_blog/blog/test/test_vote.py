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


@pytest.mark.django_db
def test_counting():
    subj = 'Jump over the campfire.'
    for _ in range(3):
        models.Vote.in_favour(subj)
    for _ in range(5):
        models.Vote.against(subj)
    for _ in range(7):
        models.Vote.against('Burn money')
    assert models.Vote.results_for(subj) == {'in favour': 3, 'against': 5}


@pytest.mark.django_db
def test_on_unknown_subject():
    assert models.Vote.results_for('???') == {'in favour': 0, 'against': 0}
