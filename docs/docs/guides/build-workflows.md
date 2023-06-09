# Build Workflows

Director separates the tasks logic from the workflows definition by providing a
simple YAML syntax.

!!! note
    A workflow declaration in Celery Director is always composed of 2 parts (the project name and the workflow name) separated by a dot, for instance: `project.workflow`.

    In the following examples the name of the workflows has been capitalized, but this is just a convention we use at OVHcloud and it's not mandatory.

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

You can use the `periodic > interval` key with a number argument (in seconds):

```yaml
example.CHAIN:
  tasks:
    - A
    - B
    - C
  periodic:
    interval: 60
```

You can also use the `periodic > crontab` key with a string argument:

```yaml
example.CHAIN_CRONTAB:
  tasks:
    - A
    - B
    - C
  periodic:
    crontab: "0 */3 * * *"
```

The format is the following (the [official documentation](https://docs.celeryproject.org/en/v4.4.7/userguide/periodic-tasks.html#crontab-schedules) of the `crontab` function gives some examples of each attribute):

```yaml
periodic:
  crontab: "minute hour day_of_month month_of_year day_of_week"
```

So in the first example, the *example.CHAIN* workflow will be executed **every 60 seconds** and the second one, *example.CHAIN_CRONTAB*, **every three hours**.

!!! warning
    Older versions of Celery Director (< 0.4.0) used the `periodic > schedule` key which is now deprecated.

    It is strongly advised to migrate to `periodic > interval` or `periodic > crontab` keys to set up a scheduled workflow.

    How to migrate:

    * **If your schedule is in seconds**: just rename `schedule` to `interval`;
    * **If your schedule is a crontab**: rename `schedule` to `crontab`.

        Be careful when migrating from `schedule` to `crontab`, there is also a fix to apply.
        The old `schedule` syntax incorrectly parses the string as `minute hour day_of_week day_of_month month_of_year` but the `crontab` syntax properly parses the string as `minute hour day_of_month month_of_year day_of_week`.

        For example: `0 12 1 * *` should become `0 12 * * 1` for a scheduled workflow at 12:00 UTC on Monday.

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
