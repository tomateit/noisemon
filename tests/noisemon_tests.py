import unittest
import typing

class TestIntentExtractor(unittest.TestCase):
    def setUp(self):
        self.DDDdd = DDD()

    # def test_intent_extractor_initialization(self):
    #     IntentExtractor()

    def test_intent_extractor_return_shape(self):
        ddd = self.DDD("message")
        self.assertIsInstance(ddd, typing.List)



    # def tearDown(self):
    #     self.intent_extractor.dispose()


class TestDDD(unittest.TestCase):
    def setUp(self):
        self.DDD = DDD()

    

# if __name__ == "__main__":
#     unittest.main()