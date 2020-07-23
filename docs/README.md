Docs
====

We use mkdocs to build the Celery Director documentation.

The first step is to install the requirements inside your virtualenv :

```
(venv) git clone https://github.com/ovh/director
(venv) cd director/docs
(venv) pip install mkdocs==1.0.4
(venv) pip install mkdocs-material==4.6.3
```

Then you can launch the builtins webserver :

```
(venv) mkdocs serve
INFO    -  Building documentation...
INFO    -  Cleaning site directory
[I 200117 18:15:56 server:296] Serving on http://127.0.0.1:8000
[I 200117 18:15:56 handlers:62] Start watching changes
[I 200117 18:15:56 handlers:64] Start detecting changes
```

Note that in order to built the API documentation the `director` package
must be accessible from your PYTHONPATH :

```
(venv) python setup.py develop
```
