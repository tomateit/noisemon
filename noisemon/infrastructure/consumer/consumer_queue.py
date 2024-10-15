import json
from typing import Generator

import pika
from pika.exchange_type import ExchangeType
from pydantic import AmqpDsn

from noisemon.domain.models.document import DocumentData
from noisemon.domain.services.consumer.consumer import Consumer
from noisemon.logger import logger


class ConsumerQueueImpl(Consumer):
    last_delivery_tag = None

    def __init__(self, amqp_dsn: AmqpDsn, exchange_name: str, queue_name: str):
        self.source_exchange_name = exchange_name
        self.source_queue_name = queue_name
        credentials = pika.PlainCredentials(
            username=amqp_dsn.username, password=amqp_dsn.password
        )
        parameters = pika.ConnectionParameters(
            host=amqp_dsn.host,
            port=amqp_dsn.port,
            credentials=credentials,
            connection_attempts=5,
        )
        connection = pika.BlockingConnection(parameters=parameters)
        message_properties = pika.BasicProperties(
            content_type="text/plain", delivery_mode=pika.DeliveryMode.Persistent
        )
        channel = connection.channel()
        logger.debug("Exchange and queue declaration")
        channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=ExchangeType.direct,
            durable=True,
            passive=False,  # actually do declare, rather than just check
        )
        channel.queue_declare(
            queue=queue_name,
            auto_delete=False,
            durable=True,
        )
        channel.queue_bind(
            queue=queue_name,
            exchange=exchange_name,
        )

        self.connection = connection
        self.channel = channel
        self.message_properties = message_properties

    def get_new_document(self) -> Generator[DocumentData, None, None]:
        for method_frame, properties, body in self.channel.consume(
            self.source_queue_name
        ):
            if method_frame:
                self.last_delivery_tag = method_frame.delivery_tag

                if body is None:
                    self.nack_last_page()
                    continue

                request = self._parse_incoming_body(body)

                if request is None:
                    self.nack_last_page()
                    continue

                yield request

                if self.last_delivery_tag is not None:
                    # it shall have normally been modified from the outside
                    logger.warning(
                        "Delivery tag is still present. Message was not acked!"
                    )

    def _parse_incoming_body(self, body: bytes) -> DocumentData | None:
        logger.debug(f"Got raw body len: {len(body)}")
        payload = body.decode("utf-8")
        logger.debug(f"Decoded it into: {payload[:10]}")
        data = json.loads(payload)
        logger.debug(f"Parsed into: {data.keys()}")
        new_request = DocumentData(html_data=data["content_text"])
        return new_request

    def ack_last_page(self):
        if self.last_delivery_tag is not None:
            self.channel.basic_ack(delivery_tag=self.last_delivery_tag)
            self.last_delivery_tag = None

    def nack_last_page(self):
        if self.last_delivery_tag is not None:
            self.channel.basic_nack(delivery_tag=self.last_delivery_tag)
            self.last_delivery_tag = None

    def graceful_shutdown(self):
        if self.last_delivery_tag:
            self.nack_last_page()
        requeued_messages = self.channel.cancel()
        print("Requeued %i messages" % requeued_messages)
        # Close the channel and the connection
        self.channel.close()
        self.connection.close()
