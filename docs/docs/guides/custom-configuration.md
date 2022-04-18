# Custom Configuration

Director provides a way to store and expose your own settings.

Let's take this example:

```python
import requests
from director import task

@task(name="EXTRACT")
def extract(*args, **kwargs):
    r = requests.get("https://jsonplaceholder.typicode.com/todos")
    return r.json()
```

It works, but it can be better if the URL comes from a setting.

You can do that using the `.env` file:

```
$ cat .env
[...]

# ---------- Custom config ----------
DIRECTOR_MY_URL=https://jsonplaceholder.typicode.com/todos
```

Note the `DIRECTOR_` prefix which is required to expose your custom setting. You can now access it using the `config` object:

```python
import requests
from director import config, task

@task(name="EXTRACT")
def extract(*args, **kwargs):
    r = requests.get(config.get("MY_URL"))
    return r.json()
```

!!!info
    Note the `DIRECTOR_` prefix has to be removed in your tasks (we define the `DIRECTOR_MY_URL` setting and we access it using `MY_URL`).


In addition, the github repository link in the webUI can be customized in `.env`:

```
DIRECTOR_REPO_LINK="https://github.com/ovh/celery-director"
```
