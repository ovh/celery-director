Tests
=====

To test Celery Director in real conditions we decided to use an executing `worker` :

```
$ (venv) git clone https://github.com/ovh/celery-director && cd celery-director
$ (venv) pip install -e "."
$ (venv) export DIRECTOR_HOME=`pwd`/tests/workflows/
$ (venv) director celery worker --concurrency=1
```

Configuration (database, redis...) can be customized in the `$DIRECTOR_HOME/.env` file.

You can then launch the tests in another terminal :

```
$ pip install ".[ci]"
$ pytest tests/ -v
```
