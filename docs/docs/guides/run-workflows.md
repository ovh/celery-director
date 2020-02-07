# Run Workflows

The next step after building your workflows is of course to execute them, and
Director provides several methods for that.

## Using the CLI

This method can be useful if you want to test your tasks and workflows when you
are developing them :

```
$ director workflow run ovh.MY_WORKFLOW
```

## Using the API

You can run a workflow using a POST request on the Director API. This is very
convenient if your applications are based on webservices.

The request is a **POST** on the `/api/workflows` endpoint :

```
$ curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"project":"ovh", "name": "MY_WORKFLOW", "payload": {}}' \
  http://localhost:8000/api/workflows
```

!!! info "Technical explanation"
    To really understand this feature it's important to know how native Celery works.

    Concretely Celery is constantly exchanging messages through a broker. Producers are sending
    tasks in it and workers, consuming the queue, are really executing the Python code. To
    make it work both side must be able to import the Python code (it means the producers **and**
    the consumer must be able to do `from tasks import my_task`).

    Sometimes it's difficult to allow that in distributed environment. Director solves this problem
    by providing an endpoint used to execute a workflow and its tasks, so there's no more need to
    have the modules available in the producer's PYTHON_PATH.

## Using the periodic scheduling

A workflow can also be execute periodically without any manual action from the user. Director provides
a [simple YAML syntax](build-workflows.md#periodic-workflows) for that.