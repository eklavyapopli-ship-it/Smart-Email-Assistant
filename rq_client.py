from redis import Redis
from rq import Queue

queue = Queue(
    host="localhost",
    port="6379"
)