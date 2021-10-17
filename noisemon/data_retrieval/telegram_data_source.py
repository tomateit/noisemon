import time
import logging
import zmq
import telethon
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon import events
from settings import settings
from schemas import DataChunk
import asyncio
from functools import lru_cache
# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.


class TelegramDataSource():
    client: TelegramClient
    context: zmq.Context
    socket: zmq.Socket

    def __init__(self):
        pass

    async def connect_to_telegram(self):
        api_id = settings.TELEGRAM_API_ID
        api_hash = settings.TELEGRAM_API_HASH
        self.client = TelegramClient('noisemon_session', api_id, api_hash)
        await self.client.start()
    

    def connect_to_queue(self):
        self.context = zmq.Context.instance()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.connect("tcp://127.0.0.1:2001")


    async def recieve_messages(self):
        # self.socket.send_json({"text": "lalala", "raw_text": "very raw", "origin": 123546})
        @self.client.on(events.NewMessage(forwards=False, incoming=True))
        async def event_listener(message_event):
            entity = await self.client.get_entity(message_event.message.peer_id)
            print(f"Got a message from: {entity.username}")
            if not entity.username:
                return
            # print(message_event)
            data = self.reshape_message(message_event, origin=entity.username)
            self.socket.send_json(dict(data))
        
        await self.client.run_until_disconnected()

    def run(self):
        logging.info("Telegram source is running")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        if not hasattr(self, "context"):
            self.connect_to_queue()

        if not hasattr(self, "client"):
            loop.run_until_complete(self.connect_to_telegram())

        loop.run_until_complete(self.recieve_messages())

        

    def reshape_message(self, message: telethon.tl.custom.message.Message, **kwargs) -> DataChunk:
        # print(message)
        raw_text = message.raw_text
        text = message.text
        origin = "https://t.me/" + kwargs["origin"] + "/" + str(message.id)
        timestamp = message.date.isoformat()
        data = DataChunk(raw_text=raw_text, text=text, origin=origin, timestamp=timestamp)
        # print("------->", data)
        
        return data
    
    # @lru_cache
    # def get_username_from_id(self, id_code):
