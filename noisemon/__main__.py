import json

import pika

from noisemon.schemas import DataChunk
from noisemon.settings import settings
from noisemon.processor import Processor
from noisemon.logger import logger

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
channel.exchange_declare(
    exchange=settings.RABBITMQ_EXCHANGE,
    exchange_type="direct"
)
queue_in = channel.queue_declare(
    queue=settings.RABBITMQ_SOURCE_QUEUE,
    durable=True
)
channel.queue_bind(
    exchange=settings.RABBITMQ_EXCHANGE,
    queue=queue_in.method.queue,
    routing_key=settings.RABBITMQ_SOURCE_QUEUE,
)
logger.info("RabbitMQ channel created successfully")


def main():
    myprocessor = Processor()

    while (True):
        if channel.is_closed:
            channel.open()
        method_frame, header_frame, body = channel.basic_get(queue=settings.RABBITMQ_SOURCE_QUEUE, auto_ack=False)
        if method_frame:
            delivery_tag = method_frame.delivery_tag
            data = json.loads(body)
            data = DataChunk(**data)
            myprocessor.process_data(data)
            channel.basic_ack(delivery_tag)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        queue.channel.stop_consuming()
    finally:
        queue.gracefully_shutdown()
