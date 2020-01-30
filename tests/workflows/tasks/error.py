from director import task


@task(name="TASK_ERROR")
def task_error(*args, **kwargs):
    print(1 / 0)
