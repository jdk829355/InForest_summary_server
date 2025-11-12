'''
url에 대한 요청 날리고 subscribe 통해 진행상황 알림
1. main.py에서 task 등록
2. worker.py에서 task 수행
3. tasks.py에서 실제 작업 수행
4. summarize.py에서 요약 작업 수행
5. redis pubsub 통해 진행상황 알림
6. 여기서 요약본 출력
'''

import requests
from redis import Redis
import os
from enum import Enum
import dotenv

dotenv.load_dotenv()

redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_password = os.getenv("REDIS_PASSWORD")
redis_conn = Redis(host=str(redis_host), port=int(str(redis_port)), password=str(redis_password))
pubsub = redis_conn.pubsub()

class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

def test_summarize_task(url, tree_id):
    # 1. task 등록
    response = requests.post("http://localhost:8000/task", json={"url": url, "tree_id": tree_id})
    if response.status_code != 200:
        print("Failed to create task:", response.text)
        return
    # 2. 진행상황 subscribe
    pubsub.subscribe(tree_id)
    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"메시지 수신: {message['data'].decode()}")
            if message['data'].decode() == TaskStatus.COMPLETED:
                print("요약 작업 완료!")
                break
            elif message['data'].decode() == TaskStatus.FAILED:
                print("요약 작업 실패!")
                break
        elif message['type'] == 'subscribe':
            print(f"채널 '{message['channel'].decode()}' 구독 완료.")

if __name__ == "__main__":
    test_url = "https://heroeswillnotdie.tistory.com/23"
    test_tree_id = "test"
    test_summarize_task(test_url, test_tree_id)