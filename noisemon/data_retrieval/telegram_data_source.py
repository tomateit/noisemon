import time
import logging
import zmq
import telethon
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon import events
from settings import settings
from models.data_chunk import DataChunk
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

    async def initialize_account(self):
        # 1. Get all subscriprion on channel
        all_subscriptions_map = dict()
        async for dialog in self.client.iter_dialogs():
            if not dialog.is_group and dialog.is_channel:
                entity = await self.client.get_entity(dialog.id)
                username = entity.username
                if username == "telegram":
                    continue
                print(dialog.name, dialog.id, username)
                all_subscriptions_map[username] = entity
        
        target_subscriptions = set()
        for channel in settings.TelegramConfig.get_channels_list():
            target_subscriptions.add(channel)
            print(channel)
        
        # 2. Compare with target state list
        shall_be_subscribed = target_subscriptions.difference(all_subscriptions_map.keys())
        shall_be_unsubscribed = set(all_subscriptions_map.keys()).difference(target_subscriptions)
        
        # 3. Actualize account state
        print("This channels shall be added: ", shall_be_subscribed)
        for channel in shall_be_subscribed:
            await self.client(JoinChannelRequest(channel))

        print("This channels shall be quit: ", shall_be_unsubscribed)
        for username in shall_be_unsubscribed:
            await self.client(LeaveChannelRequest(all_subscriptions_map[username]))


    async def recieve_messages(self):
        # self.socket.send_json({"text": "lalala", "raw_text": "very raw", "origin": 123546})
        @self.client.on(events.NewMessage(forwards=False, incoming=True))
        async def event_listener(message_event):
            # print(message_event)
            # entity = await self.client.get_entity(message_event.message.peer_id)
            # origin = entity.username
            data = self.reshape_message(message_event)

            self.socket.send_json(dict(data))
        
        # time.sleep(3)
        # for message in await self.client.get_messages():
        #     data = self.reshape_message(message)
        #     self.socket.send_json(data)

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

        

    def reshape_message(self, message: telethon.tl.custom.message.Message) -> DataChunk:
        raw_text = message.raw_text
        text = message.text
        origin = message.chat_id
        return DataChunk(raw_text=raw_text, text=text, origin=origin)
    
    # @lru_cache
    # def get_username_from_id(self, id_code):
