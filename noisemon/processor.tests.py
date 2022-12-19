import unittest

from noisemon.processor import Processor


class TestProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = Processor()

    def test_processor_initialization(self):
        Processor()

    def tearDown(self):
        self.processor.socket.close()


if __name__ == "__main__":
    unittest.main()
