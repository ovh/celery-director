# Build Workflows

Director separates the tasks logic from the workflows definition by providing a
simple YAML syntax.

Let's imagine the following tasks :

```python
# tasks/example.py
from director import task

@task(name="A")
def a(*args, **kwargs):
    pass

@task(name="B")
def b(*args, **kwargs):
    pass

@task(name="C")
def c(*args, **kwargs):
    pass
```

## Chaining multiple tasks

Chaining these tasks in the `workflows.yml` file is pretty simple :

```yaml
# Chain example
#
# +-------+      +-------+      +-------+
# |   A   +----->+   B   +----->+   C   |
# +-------+      +-------+      +-------+
#
example.CHAIN:
  tasks:
    - A
    - B
    - C
```

In this example each task will be executed one after the other : first the task A will
be executed, then the task B and finally the task C.

## Launch tasks in parallel

Sometimes you need to execute some tasks in parallel to improve your workflow performance.
The `type: group` keywords can be used to handle this canvas :

```yaml
# Group example
#                +-------+
#            +-->+   B   |
# +-------+  |   +-------+
# +   A   +--+
# +-------+  |   +-------+
#            +-->+   C   |
#                +-------+
example.GROUP:
  tasks:
    - A
    - GROUP_1:
        type: group
        tasks:
          - B
          - C
```

In this example the group is named **GROUP_1** but it can be anything. The important
is to keep unique names in case of multiple groups in your workflow.

## Periodic workflows

Celery provides a scheduler used to periodically execute some tasks. This scheduler is named
the [Celery beat](https://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html).

Director allows you to periodically schedule a whole workflow using a simple YAML syntax.

First example:

```yaml
example.CHAIN:
  tasks:
    - A
    - B
    - C
  periodic:
    schedule: 60
```

Second example:

```yaml
example.CHAIN_CRONTAB:
  tasks:
    - A
    - B
    - C
  periodic:
    schedule: "0 */3 * * *"
```

The `periodic > schedule` key takes an integer (unity is the second) or a string argument
([crontab](https://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html#crontab-schedules)
syntax). So in the first example, the *example.CHAIN* worflow will be executed **every 60 seconds**
and the second one, *example.CHAIN_CRONTAB*, **every three hours**.

Please note that the scheduler must be started to handle periodic workflows :

```
$ director celery beat
```

!!! tip
    Celery also accepts the `-B` option when launching a worker :

    ```
    $ director celery worker --loglevel=INFO -B
    ```

    This way you can start your worker and scheduler instances using a single command.
    Please note this option is only to use during your development, otherwise use the `celery
    beat` command.

## Use of queues in Workflows

With director, you can set queues for workflows. All workflow's tasks will use the same queue:

```yaml
example.ETL:
  tasks:
    - A
    - B
    - C
  queue: q1
```

You need the start Celery worker instance with the `--queues` option:

```bash
$ director celery worker --loglevel=INFO --queues=q1
```
