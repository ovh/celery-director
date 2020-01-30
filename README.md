Celery Director
===============

Celery Director is a tool used to easily manage workflows with Celery :

- workflows written in YAML
- execution and visualization using API, WebUI and CLI
- manual and periodic executions

![Celery Director](director.png)

Installation
------------

Director requires Python 3+ :

```
$ pip install celery-director
```

Usage
-----

Celery Director provides an `init` command used to bootstrap a project :

```
$ director init ~/workflows
[*] Project created in /Users/ovh/workflows
You can now export the DIRECTOR_HOME environment variable
```

An example has been generated in the `tasks/etl.py` file :

```
$ cat tasks/etl.py
from director import task


@task(name="EXTRACT")
def extract(*args, **kwargs):
    print("Extracting data")


@task(name="TRANSFORM")
def transform(*args, **kwargs):
    print("Transforming data")


@task(name="LOAD")
def load(*args, **kwargs):
    print("Loading data")
```

The `workflows.yml` contains a simple ETL executing each task one after the other :

```
$ cat workflows.yml
---
# Simple ETL example
#
# +-----------+      +-------------+      +--------+
# |  EXTRACT  +----->+  TRANSFORM  +----->+  LOAD  |
# +-----------+      +-------------+      +--------+
#
ovh.SIMPLE_ETL:
  tasks:
    - EXTRACT
    - TRANSFORM
    - LOAD
```

You need to update the `.env` file with your own configuration (database, redis...) and create the director database :

```
$ director upgradedb
```

You can now launch a worker and the webserver in 2 different shells :

```
$ director celery worker
$ director webserver
```

The webserver is available at http://localhost:8000.

Manually Execution
------------------

Each workflow can be manually executed in different ways.

**Using the CLI**

```
$ director workflow run ovh.SIMPLE_ETL '{}'
```

**Using the API**

```
$ curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"project":"ovh", "name": "SIMPLE_ETL", "payload": {}}' \
  http://localhost:8000/api/workflows
```

**Using the WebUI**

*TODO*

Periodic Execution
------------------

Celery Director can also periodically execute your workflow by specifying it in the `workflows.yml`. For example this workflow will be executed every **60 seconds** :

```
ovh.SIMPLE_ETL:
  tasks:
    - EXTRACT
    - TRANSFORM
    - LOAD
  periodic:
    schedule: 60
```

Note that the scheduler must be started to handle periodic workflows :

```
$ director celery beat
```

Group tasks
-----------

You can also group tasks together using the following syntax :

```
# Group ETL example
#                                         +--------------+
#                                     +-->+  LOAD_IN_DB  |
# +-----------+      +-------------+  |   +--------------+
# |  EXTRACT  +----->+  TRANSFORM  +--+
# +-----------+      +-------------+  |   +--------------+
#                                     +-->+  LOAD_IN_FS  |
#                                         +--------------+
ovh.GROUP_ETL:
  tasks:
    - EXTRACT
    - TRANSFORM
    - LOADS:
        type: group
        tasks:
          - LOAD_IN_DB
          - LOAD_IN_FS
```

Here the **LOADS** name can be anything and is just here to group the LOAD_IN_DB and LOAD_IN_FS tasks.

Of course you can have several groups in your workflow :

```
# Multiple Groups Example
#
# +--------------------+                           +--------------+
# |  EXTRACT_FROM_API  +--+                    +-->+  LOAD_IN_DB  |
# +--------------------+  |   +-------------+  |   +--------------+
#                         +-->+  TRANSFORM  +--+
# +--------------------+  |   +-------------+  |   +--------------+
# |  EXTRACT_FROM_CSV  +--+                    +-->+  LOAD_IN_FS  |
# +--------------------+                           +--------------+
#
ovh.GROUPS_ETL:
  tasks:
    - EXTRACTS:
        type: group
        tasks:
          - EXTRACT_FROM_API
          - EXTRACT_FROM_CSV
    - TRANSFORM
    - LOADS:
        type: group
        tasks:
          - LOAD_IN_DB
          - LOAD_IN_FS
```

LICENSE
-------

License

See https://github.com/ovh/celery-director/blob/master/LICENSE
