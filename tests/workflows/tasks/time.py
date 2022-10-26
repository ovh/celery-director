from director import task
import time


@task(name="DELAY")
def delay(*args, **kwargs):
    print("Task wich took time, lot of time...")
    time.sleep(300)
    print("Delay finished")
