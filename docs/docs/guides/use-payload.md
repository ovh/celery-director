# Use Payload

Most of the time your workflow and their tasks will not be *static* but will
depend on some payload to work.

For example you can have the following workflow :

```yaml
product.ORDER:
  tasks:
    - ORDER_PRODUCT
    - SEND_MAIL
```

This usecase is simple :

1. the fist task creates an order about a specific product,
2. then an email is sent to the customer about its order details.

## Send payload

Of course the tasks need some data to work (the product and the user IDs
for example). This is possible in Director using the **payload** field :

```
$ director workflow run product.ORDER '{"user": 1234, "product": 1000}'
```

or

```
$ curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"project": "product", "name": "ORDER", "payload": {"user": 1234, "product": 1000}}' \
  http://localhost:8000/api/workflows
```

## Handle payload

You can handle the payload in the code using the **kwargs** dictionnary :

```python
@task(name="ORDER_PRODUCT")
def order_product(*args, **kwargs):
    order = Order(
      user=kwargs["payload"]["user"],
      product=kwargs["payload"]["product"]
    ).save()
    return {"id": order.id}

@task(name="SEND_MAIL")
def send_mail(*args, **kwargs):
    order_id = args[0]["id"]
    mail = Mail(
      title=f"Your order #{order_id} has been received",
      user=kwargs["payload"]["user"]
    )
    mail.send()
```

As you can see the payload is forwarded to **all the tasks** contained in
your workflow.

## Periodic workflows

Celery Director provides a YAML syntax to [periodically schedule a workflow](build-workflows.md#periodic-workflows).
If your workflow needs a payload to work, you can send it default values :

```yaml
users.UPDATE_CACHE:
  tasks:
    - UPDATE_CACHE
  periodic:
    schedule: 3600
    payload: {"user": False}
```

The corresponding task can easily handle this default value :

```python
@task(name="UPDATE_CACHE")
def update_cache(*args, **kwargs):
    user = kwargs["payload"]["user"]

    if not user:
        return update_all_users()
    return update_user(user)
```

This way the whole list of users will be updated every hours, and a manual update
can be done on a specific user :

```
$ director workflow run users.UPDATE_CACHE '{"user": "john.doe"}'
```
