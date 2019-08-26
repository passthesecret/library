import unittest
from passthesecret.manager import Manager


class TestManager(unittest.TestCase):
    def setUp(self):
        self.manager = Manager()

    def test_create_secret(self):
        secret_response = self.manager.create_secret('Thisisapassword!', 86400, False)
        self.assertEqual(secret_response['view_request_string'], 'SomeCode')
        self.assertEqual(secret_response['wipe_request_string'], 'SomeCode')


if __name__ == '__main__':
    unittest.main()
