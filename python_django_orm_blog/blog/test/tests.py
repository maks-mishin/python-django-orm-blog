import pytest
from python_django_orm_blog.blog import models


def make_tasks(graph, parent=None):
    for value, sub_graph in graph.items():
        task = models.Task.objects.create(value=value, parent=parent)
        make_tasks(sub_graph, parent=task)


@pytest.mark.django_db
def test_without_cycles():
    make_tasks({
        'buy some bread': {},
        'learn Python': {
            'buy a book': {},
            'complete the Python profession on Hexlet': {
                'register on Hexlet': {},
            },
        },
    })

    task1 = models.Task.objects.get(value='buy some bread')
    assert task1.root is task1

    task2 = models.Task.objects.get(value='register on Hexlet')
    assert task2.root.value == 'learn Python'


@pytest.mark.django_db
def test_with_cycles():
    make_tasks({
        'A': {
            'B': {
                'C': {},
                'D': {},
            },
        },
    })

    task_a = models.Task.objects.get(value='A')
    task_b = models.Task.objects.get(value='B')
    task_c = models.Task.objects.get(value='C')
    # завязываем узел
    task_a.parent = task_c
    task_a.save()

    task_d = models.Task.objects.get(value='D')
    with pytest.raises(models.CycleInGraphError) as exc_info:
        task_d.root
    # исключение должно содержать id задачи,
    # которая уже встречалась на пути поиска корневой задачи
    # D -> B -> A -> C -> B
    #                     ^ встречается второй раз!
    assert exc_info.value.args[0] == task_b.id
