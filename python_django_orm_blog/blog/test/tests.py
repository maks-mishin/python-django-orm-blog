import django.db
import pytest

from python_django_orm_blog.blog import models


def work_on(*args, project_id):
    return all(
        models.Worker.objects.get(id=worker_id).project_id == project_id
        for worker_id in args
    )


@pytest.mark.django_db
def test_project_reorganize():
    alice, bob, john, tom = [
        models.Worker.objects.create(name=name).id
        for name in ('Alice', 'Bob', 'John', 'Tom')
    ]

    site, wiki, crm = [
        models.Project.objects.create(name=name).id
        for name in ('Site', 'Wiki', 'Crm')
    ]

    models.Project.reorganize({
        alice: site,
        bob: site,
        john: wiki,
        tom: crm,
    })

    assert work_on(alice, bob, project_id=site)
    assert work_on(john, project_id=wiki)
    assert work_on(tom, project_id=crm)

    models.Project.reorganize({
        alice: crm,
        bob: crm,
        john: crm,
    })

    assert work_on(alice, bob, john, project_id=crm)
    assert work_on(tom, project_id=None)


@pytest.mark.django_db(transaction=True)
def test_project_reorganize_on_bad_data():
    time_machine = models.Project.objects.create(name='Time Machine').id
    marty = models.Worker.objects.create(name='Marty').id
    emmet = models.Worker.objects.create(
        name='Emmet',
        project_id=time_machine,
    ).id

    with pytest.raises(django.db.IntegrityError):
        models.Project.reorganize({
            marty: time_machine,
            emmet: 42,  # несуществующий проект!
        })

    # исходные назначения не должны были измениться
    assert work_on(emmet, project_id=time_machine)
    assert work_on(marty, project_id=None)
