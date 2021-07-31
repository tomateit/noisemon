import zmq
from models.data_chunk import DataChunk

class Processor():
    def __init__(self):
        pass

    def connect_to_queue(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://127.0.0.1:2000")
        self.socket.setsockopt(zmq.SUBSCRIBE, "")

    async def run(self):
        for data in await self.socket.recv_json():
            self.process_data(data)

    def process_data(self, data: DataChunk):
        pass