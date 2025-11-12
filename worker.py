from redis import Redis
from rq import Worker, Queue
import dotenv
import os
import time

dotenv.load_dotenv()
redis_host = os.getenv("REDIS_HOST")
redis_host = redis_host if redis_host is not None else exit()
redis_port = os.getenv("REDIS_PORT")
redis_port = redis_port if redis_port is not None else exit()
redis_password = os.getenv("REDIS_PASSWORD")
redis_password = redis_password if redis_password is not None else exit()

redis_options = {
    "host": redis_host,
    "port": int(redis_port),
    "password": redis_password
}
print("Redis Options:", redis_options)

queue = Queue(connection=Redis(**redis_options))
print("queue created")


for _ in range(10):
    time.sleep(2)
    try:
        worker = Worker([queue], connection=Redis(**redis_options))
        print("worker created")
        worker.work(with_scheduler=True)
        print("Worker finished successfully")
        break
    except Exception as e:
        pass