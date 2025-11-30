from fastapi import FastAPI
from pydantic import BaseModel
from redis import Redis
from rq import Queue
import tasks
from dotenv import load_dotenv
import os

load_dotenv("./.env")
# TODO github에 올리기
app = FastAPI()

class TaskRequest(BaseModel):
    url: str
    tree_id: str

class TaskResponse(BaseModel):
    tree_id: str
    success: bool

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

redis_conn = Redis(**redis_options)
queue = Queue(connection=redis_conn)

@app.get('/')
def welcome_root_get():
    return {"message": "Welcome to the Task Queue API"}

@app.post('/task')
def welcome_root(req: TaskRequest):
    # 이미 작업큐에 등록된 상태인지 확인
    existing_job_id = redis_conn.get(f"task_status:{req.tree_id}")
    if existing_job_id is not None:
        return TaskResponse(tree_id=req.tree_id, success=False)

    queue.enqueue(tasks.summarize, req.tree_id, req.url)
    return TaskResponse(tree_id=req.tree_id, success=True)
    