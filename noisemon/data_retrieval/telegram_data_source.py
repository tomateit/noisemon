import time
import logging
import zmq
import telethon
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from settings import settings
from models.data_chunk import DataChunk
# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.


class TelegramDataSource():
    client: TelegramClient
    context: zmq.Context
    socket: zmq.Socket

    def __init__(self):
        pass

    def connect_to_telegram(self):
        # api_id = settings.get("TELEGRAM_API_ID")
        # api_hash = settings.get("TELEGRAM_API_HASH")
        # self.client = TelegramClient('noisemon_session', api_id, api_hash)
        # self.client.start()
        pass

    def connect_to_queue(self):
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.connect("tcp://127.0.0.1:2001")

    async def initialize_account(self):
        # Subscribe here
        for channel in settings.TelegramConfig.get_channels_list():
            print(channel)
            # await self.client(JoinChannelRequest(channel))

    def run(self):
        logging.info("Telegram source is running")
        if not hasattr(self, "context"):
            self.connect_to_queue()

        if not hasattr(self, "client"):
            self.connect_to_telegram()

        while True:
            self.socket.send_json({"text": "lalala", "raw_text": "very raw", "origin": 123546})
            time.sleep(3)
        # for message in await self.client.get_messages():
        #     data = self.reshape_message(message)
        #     self.socket.send_json(data)

    def reshape_message(self, message: telethon.tl.custom.message.Message) -> DataChunk:
        raw_text = message.raw_text
        text = message.text
        origin = message.chat_id
        return DataChunk(raw_text=raw_text, text=text, origin=origin)