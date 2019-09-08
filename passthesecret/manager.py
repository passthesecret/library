from cryptography.fernet import Fernet
import os
import uuid

class Manager(object):

    database = None

    def __init__(self, database):
        self.database = database

    def get_free_secret_id(self):

    def create_secret(self, secret, expire_in_seconds, burn_after_reading):
        # Hardcode some random value temporarily
        # Will have to figure out how to generate this, or have this set by an admin
        # on first start.
        wrap_key = os.environ['PTS_WRAP_KEY'].encode('UTF-8')
        view_key = Fernet.generate_key()
        wipe_key = Fernet.generate_key()
        wrap_f = Fernet(wrap_key)
        view_f = Fernet(view_key)
        wipe_f = Fernet(wipe_key)
        # Need to think about if there is a security risk of having known short plaintext.
        # Could have some other plaintext text that could be sort of known or otherwise validated
        # A super simple example could be any string that is X characters, or only odd numbers or something.
        # Is that method tangibly different from just encrypting it again?
        wipe = str(uuid.uuid4())
        # Store the two tokens in the database with the secret_id as the Primary Key
        view_token = wrap_f.encrypt(view_f.encrypt(secret.encode('UTF-8'))).decode('UTF-8')
        wipe_token = wrap_f.encrypt(wipe_f.encrypt(wipe.encode('UTF-8'))).decode('UTF-8')
        secret_id = self.database.create_secret_entry()
        view_request_string = f"{secret_id}{view_key.decode('UTF-8')}"
        wipe_request_string = f"{secret_id}{wipe_key.decode('UTF-8')}"
        return {
            'view_request_string': view_request_string,
            'wipe_request_string': wipe_request_string
        }

    def get_secret(self, request_string):
        if len(request_string) != 76:
            # Request Strings are always UUIDs without dashes (32 char) + Fernet Generated Key (44 char) = 76 char
            # Figure out how to articulate errors later
            return {
                'error': 'Malformed Request String'
            }
        # Double check these
        secret_id = request_string[:32]
        encryption_key = request_string[32:]
        wrap_key = '2PVSb6EpnElctRLqvn0dBBgX7sC2P2Oo70E1rE7ydDA='.encode('UTF-8')
        wrap_f = Fernet(wrap_key)
        decrypt_f = Fernet(encryption_key)

        secret_data = decrypt_f.decrypt(secret_id)
        return secret_data
