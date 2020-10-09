# Quickstart

## Generate the project

One of the Director goals is to facilitate the usage of Celery. For that we wanted to
simplify the initialization of a Celery project by removing all the long an boring
*boilerplate* steps (application creation, broker configuration...).

So the first thing to do is to generate a project using the `director init` command :

```text
$ director init workflows
[*] Project created in /home/director/workflows
[*] Do not forget to initialize the database
You can now export the DIRECTOR_HOME environment variable
```

!!! info
    Because you can have several projects in your machine, Director needs to know what
    project you want to target when using the `director` command. So don't forget to
    set your `DIRECTOR_HOME` environment variable :

    ```
    $ export DIRECTOR_HOME="/home/director/workflows"
    ```

Director created the following structure for you containing a simple example :

```
.env                # The configuration file.
workflows.yml       # The workflows definition.
tasks/
    etl.py          # A file containing some tasks.
    ...             # Other files containing other tasks.
```

The Python files in the `tasks` folder will contain your Celery tasks :

```python
from director import task


@task(name="EXTRACT")
def extract(*args, **kwargs):
    print("Extracting data")
```

While the `workflows.yml` file will be used to combine them into workflows :

```yaml
example.ETL:
  tasks:
    - EXTRACT
    - TRANSFORM
    - LOAD
```

## Configure the database

Director needs a connection to a relational database to store the dependencies
between your tasks.

Adjust the `DIRECTOR_DATABASE_URI` variable in the `.env` file and generate the database :

Possible values for the `DIRECTOR_DATABASE_URI` variable:
```shell
DIRECTOR_DATABASE_URI="postgresql://user:password@hostname:port/database"           # Using PostgreSQL
DIRECTOR_DATABASE_URI="mysql+mysqlconnector://user:password@hostname:port/database" # Using MySQL
DIRECTOR_DATABASE_URI="sqlite:////path/to/your/database.db"                         # Using SQLite
```

Generate the database:
```
$ director db upgrade
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 70631f8bcff3, Init database
```

## Run the workflow

The `workflow` command can be used to manage your workflows.

**List**

```
$ director workflow list
+-----------------+----------+----------------------+
| Workflows (2)   | Periodic | Tasks                |
+-----------------+----------+----------------------+
| example.ETL     |    --    | EXTRACT              |
|                 |          | TRANSFORM            |
|                 |          | LOAD                 |
+-----------------+----------+----------------------+
| example.RANDOMS |    --    | Group GROUP_RANDOMS: |
|                 |          |  └ RANDOM            |
|                 |          |  └ RANDOM            |
|                 |          | ADD                  |
+-----------------+----------+----------------------+
```

**Run**

```
$ director workflow run example.ETL
```

## Execute the tasks

A Celery worker instance needs to be started to consume the broker and execute the tasks :

```
$ director celery worker --loglevel=INFO
```

## Display the result

You can finally start the webserver to track the tasks evolution :

```
$ director webserver
```

The WebUI is available by default on [http://127.0.0.1:8000](http://127.0.0.1:8000) :

![Celery Director ETL](img/etl.png)

!!! note "Change default parameters"
    The `webserver` command forwards the arguments to gunicorn. For instance the
    binding can be easily changed : `director webserver -b 0.0.0.0:5000`.
