from director import task
import requests
import re

@task(name="CRAWL")
def extract(*args, **kwargs):
    print("START")
    payload = kwargs["payload"]
    resp = requests.get(payload.get('url'))
    return resp.content.decode('latin-1', 'utf-8')


@task(name="FIND_URL")
def transform(*args, **kwargs):
    print("Transforming data")
    #Find all links
    result = re.findall('<a href="(.*?)">(.*?)</a>', str(args[0]))
    return ''.join(''.join(tup) for tup in result)


@task(name="SAVE_FILE")
def load(*args, **kwargs):
    print("WRITE TO FILE")
    with open('html.txt', 'w') as f:
        f.write(args[0])
