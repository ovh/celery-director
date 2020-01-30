from director import task


@task(name="TASK_A")
def task_a(*args, **kwargs):
    return "task_a"


@task(name="TASK_B")
def task_b(*args, **kwargs):
    return "task_b"


@task(name="TASK_C")
def task_c(*args, **kwargs):
    return "task_c"
