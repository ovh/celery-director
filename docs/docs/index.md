# Celery Director Documentation

Director is a simple and rapid framework used to manage tasks and build workflows using Celery.

![Celery Director](img/director.png)

## Features

The objective is to make Celery easier to use by providing :

- a WebUI to track the tasks states,
- an API and a CLI to manage and execute the workflows,
- a YAML syntax used to combine tasks into workflows,
- the ability to periodically launch a whole workflow,
- and many others.

!!! info
    Director is built on top of the excellent [Celery library](http://docs.celeryproject.org/en/latest/index.html).
    All the orchestration engine has not been changed : we didn't want to reinvent the wheel but
    provide an easy tool to use Celery.

    It means that all your existing tasks can easily be migrated to Director. Furthermore the
    documentation of the tasks and all the features powered by Celery like the **rate limiting**,
    the **task exception retrying** or even the **queue routing** stay the same.


## Installation

Install the latest version of Director with pip (requires `Python 3.6` at least):

```bash
pip install celery-director
```

## Commands

* `director init [path]` - Create a new project.
* `director celery [worker|beat|flower]` - Start Celery daemons.
* `director webserver` - Start the webserver.
* `director workflow [list|show|run]` - Manage your project workflows.


## Project layout

    .env                # The configuration file.
    workflows.yml       # The workflows definition.
    tasks/
        example.py      # A file containing some tasks.
        ...             # Other files containing other tasks.
