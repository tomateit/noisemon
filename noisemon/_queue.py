import pika
import json
import logging

from settings import settings
from schemas import DataChunk


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Queue():
    connection: pika.BlockingConnection
    channel: pika.channel

    def __init__(self, **kwargs):
        self.credentials = pika.PlainCredentials(
            settings.RABBITMQ_USERNAME,
            settings.RABBITMQ_PASSWORD,
        )
        
        self.connection_parameters = pika.ConnectionParameters(
            host=settings.RABBITMQ_URI,
            credentials=self.credentials,
            heartbeat=600,
            blocked_connection_timeout=300,
            connection_attempts=5, 
            retry_delay=3
        )

        self.connection = pika.BlockingConnection(self.connection_parameters)
        logger.info("RabbitMQ connection created successfully")
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=settings.RABBITMQ_EXCHANGE, exchange_type='direct')
        queue_out = self.channel.queue_declare(queue=settings.RABBITMQ_SOURCE_QUEUE, durable=True)
        self.channel.queue_bind(exchange=settings.RABBITMQ_EXCHANGE, queue=queue_out.method.queue, routing_key=settings.RABBITMQ_SOURCE_QUEUE)
        logger.info("RabbitMQ channel created successfully")

    
    def gracefully_shutdown(self):
        # Cancel the consumer and return any pending messages
        logger.info("Shutting down bus adapter")
        requeued_messages = self.channel.cancel()
        print(f"Requeued {requeued_messages} messages")
        self.connection.close()

    def on_message_wrapper(self, callback):
        def on_message(channel, method_frame, header_frame, body):
            logger.debug("|---- BEGIN ON MESSAGE CALLBACK")
            try:
                delivery_tag = method_frame.delivery_tag
                data = json.loads(body)
                data = DataChunk(**data)
                callback(data)

                if self.channel.is_open:
                    self.channel.basic_ack(delivery_tag)
            except Exception as e:
                logger.exception(e)
            logger.debug("|---- END ON MESSAGE CALLBACK")

        return on_message
        
    def register_consumer_callback(self, callback):
        on_message_callback = self.on_message_wrapper(callback)

        self.channel.basic_consume(on_message_callback=on_message_callback, queue=settings.RABBITMQ_SOURCE_QUEUE)
        logger.debug("Registered consumer callback")