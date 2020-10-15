Tests
=====

To test Celery Director in real conditions we decided to use an executing `worker` :

```
$ (venv) git clone https://github.com/ovh/director && cd director
$ (venv) python setup.py develop
$ (venv) export DIRECTOR_HOME=`pwd`/tests/workflows/
$ (venv) director celery worker -P solo -D
```

Configuration (database, redis...) can be customized in the `$DIRECTOR_HOME/.env` file.

You can then launch the tests in another terminal :

```
$ pip install pytest==5.3.5
$ pytest tests/ -v
```
