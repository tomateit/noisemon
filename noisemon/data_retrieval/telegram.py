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
        api_id = settings.get("TELEGRAM_API_ID")
        api_hash = settings.get("TELEGRAM_API_HASH")
        self.client = TelegramClient('noisemon_session', api_id, api_hash)
        self.client.start()

    def connect_to_queue(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://127.0.0.1:2000")

    async def initialize_account(self):
        # Subscribe here
        for channel in settings.TelegramConfig.get_channels_list():
            await self.client(JoinChannelRequest(channel))

    async def run(self):
        for message in await self.client.get_messages():
            data = self.reshape_message(message)
            self.socket.send_json(data)

    def reshape_message(self, message: telethon.tl.custom.message.Message) -> DataChunk:
        raw_text = message.raw_text
        text = message.text
        origin = message.chat_id
        return DataChunk(raw_text=raw_text, text=text, origin=origin)