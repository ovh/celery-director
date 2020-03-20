from director import task


@task(name="STR")
def ret_str(*args, **kwargs):
    return "return_value"


@task(name="INT")
def ret_int(*args, **kwargs):
    return 1234


@task(name="LIST")
def ret_list(*args, **kwargs):
    return ["jack", "sape", "guido"]


@task(name="NONE")
def ret_none(*args, **kwargs):
    return None


@task(name="DICT")
def ret_dict(*args, **kwargs):
    return {"foo": "bar"}


@task(name="NESTED")
def ret_nested(*args, **kwargs):
    return {
        "jack": 4098,
        "sape": 4139,
        "guido": 4127,
        "nested": {"foo": "bar"},
        "none": None,
        "list": ["jack", "sape", "guido"],
    }
