import unittest
import zmq

from .processor import Processor


class TestProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = Processor()

    def test_processor_initialization(self):
        Processor()



    def test_processor_queue_connection(self):
        p = Processor()
        self.assertFalse(hasattr(self.processor, "socket"))
        p.connect_to_queue()
        self.assertIsInstance(p.socket, zmq.Socket)
        # self.processor.connect_to_queue()
        # self.assertIsInstance(self.processor.socket, zmq.Socket)



    def tearDown(self):
        self.processor.socket.close()



if __name__ == "__main__":
    unittest.main()