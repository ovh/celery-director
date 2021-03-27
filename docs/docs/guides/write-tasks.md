# Write Tasks

Director is a wrapper around Celery, so creating tasks with it is *almost* the same
as creating tasks for pure Celery.

## Create a task

In pure Celery you had to create a Celery application object (`app = Celery(...)`) and use
the `app.task()` decorator to transform Python function into Celery tasks.

This work has already be done for you in Director, so you just have to transform your function
using the `director.task` decorator :

```python
# tasks/example.py
from director import task


@task(name="TASK_EXAMPLE")
def my_task(*args, **kwargs):
    pass
```

!!! warning Task naming
    The `name` parameter in the task decorator is mandatory. Because it will be used in the YAML
    file to [combine tasks into workflows](build-workflows.md), this name **must be unique**.

## Task signature

To simplify the tasks creation, and to allow multiple workflows to reuse the same task, the
signature is always the same: `(*args, **kwargs)`.

The **kwargs** dictionary can be used to [handle the payload](use-payload.md#handle-payload)
while **args** contains the results of the task parents (of course args is empty if your task
is at the beginning of a workflow).

!!! info "Technical explanation"
    In Celery the developer can decide if a task is able to receive or not the result of its
    parents with 2 methods : **s()** and **si()**. The *i* means **immutability** and is intended
    to ignore the parents results. So normally, as a developer, you have to be carefull about the
    method to use and you also have to create your tasks signatures consequently.

    But Director has been created to simplify that! As we decided to receive the results of the
    parents in the `args` parameter we always use the `s()` method.

Here is are some concrete examples based on the following tasks:

```python
# tasks/example.py
from director import task

@task(name="A")
def a(*args, **kwargs):
    return {"result": "a_data"}

@task(name="B")
def b(*args, **kwargs):
    return {"result": "b_data"}

@task(name="C")
def c(*args, **kwargs):
    print(args)
```

The following workflows present different usecases and the output of the C task (see the
[Build Workflows](build-workflows.md) guide to understand the YAML format) :

```yaml
example.NO_PARENT:
  tasks:
    - C
# Result : (None,)

example.ONE_PARENT:
  tasks:
    - A
    - B
    - C
# Result : ({'result': 'b_data'},)

example.MULTIPLE_PARENT:
  tasks:
    - GROUP_1:
        type: group
        tasks:
          - A
          - B
    - C
# Result : ([{'result': 'a_data'}, {'result': 'b_data'}],)
```

## Bound Tasks

Celery allows use to [bind a task](https://docs.celeryproject.org/en/latest/userguide/tasks.html#bound-tasks),
providing the task instance itself as the first parameter.

In this case the signature will must contain a first parameter just before `args` and `kwargs` :

```python
# tasks/example.py
from director import task

@task(bind=True, name="BOUND_TASK")
def bound_task(self, *args, **kwargs):
    print(self.name)
```

## Celery Task Options

The `task()` decorator provided by Director is just a wrapper of the native `app.task()` decorator
provided by Celery, so all the [original options](https://docs.celeryproject.org/en/latest/userguide/tasks.html#list-of-options) are still available.

You can for example apply a *rate_limit* or even configure the max number of retries.
