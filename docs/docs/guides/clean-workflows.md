# Clean Workflows

Director allows you to permanently delete useless records of your workflows based on a retention value that is a positive integer.
For example, you can use it to keep only the 10 last records of a workflow every day at midnight.

This feature leverages [celery beat](https://docs.celeryproject.org/en/stable/userguide/periodic-tasks.html#crontab-schedules).

# Prerequisites

This feature requires that you start a Celery Beat scheduler.

You can find more details about the periodic workflows commands in [the build guide](https://ovh.github.io/celery-director/guides/build-workflows/).



Let's imagine the following workflows :

```yaml
---
# Simple ETL example
#
# +-----------+      +-------------+      +--------+
# |  EXTRACT  +----->+  TRANSFORM  +----->+  LOAD  |
# +-----------+      +-------------+      +--------+
#
example.ETL:
  tasks:
    - EXTRACT
    - TRANSFORM
    - LOAD
  retention: 2


# Group of tasks example
#
# +----------+       +----------+
# |  RANDOM  |       |  RANDOM  |
# +----+-----+       +-----+----+
#      |     +-------+     |
#      +---->+  ADD  <-----+
#            +-------+
#
example.RANDOMS:
  tasks:
    - GROUP_RANDOMS:
        type: group
        tasks:
          - RANDOM
          - RANDOM
    - ADD

```


# How it works

For each workflow that is present in your *workflows.yml*, the cleaning process will:
1. Check the retention value in *workflows.yml* and get it
2. If there is no retention there, director read the value of DIRECTOR_DEFAULT_RETENTION in *.env*
3. Director will check if the value of retention returns False. In case of a falsy value, director ignore the current workflow and loop to the next one
4. When a valid retention is found, Director will get *n* number of workflows (the retention)

5. Director will schedule the deletion of the last *n* (retention) records of the workflow.

In our example above:
- For *example.ETL* Director keep two records and delete every older entry.
- For *example.RANDOMS* Director will get the retention from DIRECTOR_DEFAULT_RETENTION in *.env*.
By default the value is set to 1000.

## Define a custom retention value
To define your own default retention, you have to modify the value of DIRECTOR_DEFAULT_RETENTION in *.env*

## Time of execution
The cleaning will be executed every day at midnight.


