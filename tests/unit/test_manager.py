import unittest
from passthesecret.manager import Manager
from passthesecret.storage.memorydb import MemoryDB


class TestManager(unittest.TestCase):

    def test_create_secret(self):
        manager = Manager(MemoryDB())
        plaintext = 'Lorem ipsum dolor sit amet'
        create_response = manager.create_secret(plaintext, 86400, False)
        self.assertEqual(len(create_response['secret_request_string']), 76)
        self.assertEqual(len(create_response['wipe_request_string']), 76)

    def test_get_secret(self):
        manager = Manager(MemoryDB())
        plaintext = 'Lorem ipsum dolor sit amet'
        create_response = manager.create_secret(plaintext, 86400, False)
        get_response = manager.get_secret(create_response['secret_request_string'])
        self.assertEqual(get_response['secret'], plaintext)


if __name__ == '__main__':
    unittest.main()
