# Cleanup Workflows

Director allows you to permanently delete useless records of your workflows based on a retention value that is a positive integer.
For example, you can use it to keep only the 10 last records of a workflow. 
The deletions start every day at midnight.

## Prerequisite

This feature requires to start a Celery beat and a worker (see [Periodic workflows](./build-workflows.md#periodic-workflows)).

## Example

```.env
# ---------- Retention -----------------
DIRECTOR_DEFAULT_RETENTION_OFFSET=-1
```

```yaml
---
# Simple ETL example
example.ETL:
  tasks:
    - EXTRACT
    - TRANSFORM
    - LOAD
  retention: 
    offset: 2

# Group of tasks example
example.RANDOMS:
  tasks:
    - GROUP_RANDOMS:
        type: group
        tasks:
          - RANDOM
          - RANDOM
    - ADD
```

- For the workflow named **example.ETL**, Director will read the retention in the .yaml configuration. Only two records will be kept, everything else will be deleted.
- For the workflow **example.RANDOMS**, Director will get the retention from `DIRECTOR_DEFAULT_RETENTION_OFFSET` in *.env*. As the value is **-1**, nothing will happen.

## Define a custom retention value
To define your own default retention, you simply have to modify the value of `DIRECTOR_DEFAULT_RETENTION_OFFSET` in *.env*.
