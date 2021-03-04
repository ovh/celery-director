# API Documentation

## **GET** `/api/workflows`

List the workflows instances.

**Example request:**

```
GET /api/workflows HTTP/1.1
Host: example.com
Accept: application/json
```

**Parameters:**

- `per_page` (optional, default: 1000): the number of workflows to return
- `page` (optional, default: 1): the page to start

**Example response:**

```
HTTP/1.1 200 OK

[
    {
        "created": "2020-02-06T13:56:51",
        "fullname": "example.ETL",
        "id": "29e7ef80-fa1b-4b91-8ccb-ef01a91601db",
        "name": "ETL",
        "payload": {"foo": "bar"},
        "periodic": false,
        "project": "example",
        "status": "pending",
        "updated": "2020-02-06T13:56:51"
    }
]
```

## **GET** `/api/workflows/<id>`

Get the details of a specific workflow instance, including its tasks.

**Example request:**

```
GET /api/workflows/29e7ef80-fa1b-4b91-8ccb-ef01a91601db HTTP/1.1
Host: example.com
Accept: application/json
```

**Example response:**

```
HTTP/1.1 200 OK

{
    "created": "2020-02-06T13:56:51",
    "fullname": "example.ETL",
    "id": "29e7ef80-fa1b-4b91-8ccb-ef01a91601db",
    "name": "ETL",
    "payload": {},
    "periodic": false,
    "project": "example",
    "status": "pending",
    "tasks": [
        {
            "created": "2020-02-06T13:56:51",
            "id": "c8606f67-9923-4c84-bc41-69efacb0c7cb",
            "key": "EXTRACT",
            "previous": [],
            "status": "pending",
            "task": "c8606f67-9923-4c84-bc41-69efacb0c7cb",
            "updated": "2020-02-06T13:56:51
        },
        {
            "created": "2020-02-06T13:56:51",
            "id": "35a2d47b-8105-4d03-becb-7eb48f8c062e",
            "key": "TRANSFORM",
            "previous": [
                "c8606f67-9923-4c84-bc41-69efacb0c7cb"
            ],
            "status": "pending",
            "task": "35a2d47b-8105-4d03-becb-7eb48f8c062e",
            "updated": "2020-02-06T13:56:51"
        },
        {
            "created": "2020-02-06T13:56:51",
            "id": "e5a8eb49-0a8c-4063-ad08-a5e9e7bd49d2",
            "key": "LOAD",
            "previous": [
                "35a2d47b-8105-4d03-becb-7eb48f8c062e"
            ],
            "status": "pending",
            "task": "e5a8eb49-0a8c-4063-ad08-a5e9e7bd49d2",
            "updated": "2020-02-06T13:56:51"
        }
    ],
    "updated": "2020-02-06T13:56:51"
}
```


## **POST** `/api/workflows`

Execute a new workflow.

**Example request:**

```
POST /api/workflows HTTP/1.1
Host: example.com
Accept: application/json

{
  "project": "example",
  "name": "ETL",
  "payload": {}
}
```

**Example response:**

```
HTTP/1.1 201 CREATED

{
    "created": "2020-02-06T14:01:02",
    "fullname": "example.ETL",
    "id": "43e70707-b661-42e1-a7df-5b98851ae340",
    "name": "ETL",
    "payload": {},
    "periodic": false,
    "project": "example",
    "status": "pending",
    "updated": "2020-02-06T14:01:02"
}
```


## **POST** `/api/workflows/<id>/relaunch`

Relaunch a workflow with the same payload.

**Example request:**

```
POST /api/workflows/29e7ef80-fa1b-4b91-8ccb-ef01a91601db/relaunch HTTP/1.1
Host: example.com
Accept: application/json
```

**Example response:**

```
HTTP/1.1 201 CREATED

{
    "created":"2021-03-04T12:27:11.245700+00:00",
    "fullname": "example.ETL",
    "id":"5afe0610-2746-413a-83d0-0099483858e6",
    "name":"ETL",
    "payload":{},
    "periodic": false,
    "project": "exemple",
    "status": "pending",
    "updated":"2021-03-04T12:27:11.245700+00:00"
}

```

## **GET** `/api/ping`

Health endpoint used to monitor Director API.

**Example request:**

```
GET /api/ping HTTP/1.1
Host: example.com
Accept: application/json
```

**Example response:**

```
HTTP/1.1 200 OK

{
  "message": "pong"
}
```
