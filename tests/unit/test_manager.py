import unittest
from passthesecret.manager import Manager
from passthesecret.storage.memorydb import MemoryDB


class TestManager(unittest.TestCase):
    def setUp(self):
        self.manager = Manager(MemoryDB())

    def test_create_secret(self):
        secret_text = 'Lorem ipsum dolor sit amet'
        create_response = self.manager.create_secret(secret_text, 86400, False)
        self.assertEqual(len(create_response['view_request_string']), 76)
        self.assertEqual(len(create_response['wipe_request_string']), 76)

    def test_get_secret(self):
        secret_text = 'Lorem ipsum dolor sit amet'
        create_response = self.manager.create_secret(secret_text, 86400, False)
        self.assertEqual(len(create_response['view_request_string']), 76)
        self.assertEqual(len(create_response['wipe_request_string']), 76)
        get_response = self.manager.get_secret(create_response['view_request_string'])
        self.assertEqual(get_response, secret_text)


if __name__ == '__main__':
    unittest.main()
