from director import task


@task(name="TASK_EXAMPLE")
def task_example(*args, **kwargs):
    return "task_example"
