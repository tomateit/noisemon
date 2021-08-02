from .telegram_data_source import TelegramDataSource
import unittest
import zmq



class TestTelegramDataSource(unittest.TestCase):
    def setUp(self):
        self.telegram = TelegramDataSource()

    def test_initialization(self):
        TelegramDataSource()

    def test_queue_connection(self):
        self.telegram.connect_to_queue()
        self.assertIsInstance(self.telegram.socket, zmq.Socket)



    def tearDown(self):
        self.telegram.socket.close()