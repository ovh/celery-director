<p align="center">
  <img alt="Celery Director logo" src="https://raw.githubusercontent.com/ovh/celery-director/master/logo.png">
</p>
<p align="center">
  <a href="https://travis-ci.org/ovh/celery-director"><img alt="Build status" src="https://travis-ci.org/ovh/celery-director.svg?branch=master"></a>
  <a href="https://www.python.org/"><img alt="Python versions" src="https://img.shields.io/badge/python-3.6%2B-blue.svg"></a>
  <a href="https://github.com/ovh/depc/blob/master/LICENSE"><img alt="License" src="https://img.shields.io/badge/license-BSD%203--Clause-blue.svg"></a>
  <a href="https://github.com/python/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>
<p align="center">
  <a href="https://raw.githubusercontent.com/ovh/celery-director/master/director.png"><img alt="Celery Director" src="https://raw.githubusercontent.com/ovh/celery-director/master/director.png"></a>
</p>

----------------

Director is a simple and rapid framework used to manage tasks and build workflows using Celery.

The objective is to make Celery easier to use by providing :

- a WebUI to track the tasks states,
- an API and a CLI to manage and execute the workflows,
- a YAML syntax used to combine tasks into workflows,
- the ability to periodically launch a whole workflow,
- and many others.

See how to use Director with the quickstart and guides in the [documentation](https://ovh.github.io/celery-director/).

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


## License

See https://github.com/ovh/celery-director/blob/master/LICENSE
