import django.db  # noqa: F401
import pytest

from python_django_orm_blog.blog.models import Island, Ship


@pytest.mark.django_db
def test_island_can_reach():
    sumatra = Island.objects.create(name='Sumatra')
    java = Island.objects.create(name='Java')
    ceylon = Island.objects.create(name='Ceylon')

    fortune = Ship.objects.create(name='Fortune')
    pearl = Ship.objects.create(name='Pearl')

    sumatra.ships.add(fortune, pearl)
    java.ships.add(fortune)
    ceylon.ships.add(pearl)

    assert sumatra.can_reach(java, by_ship=fortune)
    assert sumatra.can_reach(ceylon, by_ship=pearl)
    assert not sumatra.can_reach(java, by_ship=pearl)
    assert not sumatra.can_reach(ceylon, by_ship=fortune)
    assert not java.can_reach(ceylon, by_ship=pearl)
