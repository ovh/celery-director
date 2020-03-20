from director import task


@task(name="TASK_ERROR")
def task_error(*args, **kwargs):
    print(1 / 0)


@task(name="TASK_CELERY_ERROR")
def task_celery_error(*args, **kwargs):
    """
    This task returns a non-serializable value.
    """

    class Foo(object):
        pass

    return Foo()
