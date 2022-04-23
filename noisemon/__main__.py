import json
import logging
from pathlib import Path
from threading import Thread

import pika

from schemas import DataChunk
from settings import settings
from processor import Processor


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

credentials = pika.PlainCredentials(
    settings.RABBITMQ_USERNAME,
    settings.RABBITMQ_PASSWORD,
)

connection_parameters = pika.ConnectionParameters(
    host=settings.RABBITMQ_URI,
    credentials=credentials,
    heartbeat=600,
    blocked_connection_timeout=300,
    connection_attempts=5,
    retry_delay=3,
)

connection = pika.BlockingConnection(connection_parameters)
logger.info("RabbitMQ connection created successfully")

channel = connection.channel()
channel.exchange_declare(exchange=settings.RABBITMQ_EXCHANGE, exchange_type="direct")
queue_in = channel.queue_declare(queue=settings.RABBITMQ_SOURCE_QUEUE, durable=True)
channel.queue_bind(
    exchange=settings.RABBITMQ_EXCHANGE,
    queue=queue_in.method.queue,
    routing_key=settings.RABBITMQ_SOURCE_QUEUE,
)
logger.info("RabbitMQ channel created successfully")


def main():
    myprocessor = Processor()
    lockpath = Path("./lockfile.lock")
    
    # 1. Recv message
    # 2. Create a lock
    # 3. Spawn a thread
    # 4. While lock...

    while(True):
        if channel.is_closed:
            channel.open()
        method_frame, header_frame, body = channel.basic_get(queue=settings.RABBITMQ_SOURCE_QUEUE, auto_ack=False)
        if method_frame:
            delivery_tag = method_frame.delivery_tag
            data = json.loads(body)
            data = DataChunk(**data)
            myprocessor.process_data(data)
            channel.basic_ack(delivery_tag)

        # break
        



    

if __name__ == '__main__':
    main()
    # try:
    #     main()
    # except KeyboardInterrupt:
    #     queue.channel.stop_consuming()
    # finally:
    #     # queue.gracefully_shutdown()
    #     channel.can
