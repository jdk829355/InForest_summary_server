import os
from redis import Redis
from enum import Enum
from summarize import SummaryGenerator
from neo4j import GraphDatabase
import threading
import time


uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")



if all([uri, user, password]) is False:
    raise Exception("Neo4j 환경변수가 설정되지 않았습니다.")

redis_host = os.getenv("REDIS_HOST")
redis_port = os.getenv("REDIS_PORT")
redis_password = os.getenv("REDIS_PASSWORD")

if all([redis_host, redis_port, redis_password]) is False:
    raise Exception("Redis 환경변수가 설정되지 않았습니다.")

redis_options = {
    "host": redis_host,
    "port": int(str(redis_port)),
    "password": redis_password
}
print("Redis Options:", redis_options)



class TaskStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

# TODO 데이터베이스 연결 관리하는 패키지 새로 만들기
def get_redis_connection():
    return Redis(**redis_options)

def get_summarizer():
    summarizer = SummaryGenerator()
    return summarizer

def get_neo4j_driver():
    neo4j_driver = GraphDatabase.driver(str(uri), auth=(str(user), str(password)))
    return neo4j_driver

def update_neo4j_with_summary(tree_id, summary):
    neo4j_driver = get_neo4j_driver()
    try: 
        with neo4j_driver.session() as session:
            session.run("MATCH (t:Tree {id: $tree_id}) SET t.summary = $summary",
                        tree_id=tree_id, summary=summary)
    except Exception as e:
        raise e
def setStatus(redis_conn, tree_id, status):
    redis_conn.setex(f"task_status:{tree_id}", 3600, status)
    redis_conn.publish(tree_id, status)

def publish_task_status(tree_id, status):
    redis_conn = get_redis_connection()
    while len(status):
        setStatus(redis_conn, tree_id, status[0])
        time.sleep(3)
    return

def summarize(tree_id, url):
    # 요약 해야함
    summarizer = get_summarizer()
    redis_conn = get_redis_connection()
    status = [TaskStatus.PENDING]
    threading.Thread(target=publish_task_status, args=(tree_id, status), daemon=True).start()
    try:
        status[0] = TaskStatus.IN_PROGRESS
        result = summarizer.summarize(url, tree_id)
        # Neo4j에 요약본 저장
        update_neo4j_with_summary(tree_id, result)
    except Exception as e:
        setStatus(redis_conn, tree_id, TaskStatus.FAILED)
        raise e
    status.pop()
    setStatus(redis_conn, tree_id, TaskStatus.COMPLETED)
    return