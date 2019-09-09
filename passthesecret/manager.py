from cryptography.fernet import Fernet, InvalidToken
import os
import uuid

class Manager(object):

    database = None

    def __init__(self, database):
        self.database = database

    def create_secret(self, secret_plain, expire_in_seconds, is_consumable):
        # Set up the wipe plaintext
        wipe_plain = str(uuid.uuid4())
        # Get the encryption keys
        wrap_key = os.environ['PTS_WRAP_KEY'].encode('UTF-8')
        secret_key = Fernet.generate_key()
        wipe_key = Fernet.generate_key()
        # Set up the encryption objects with the keys
        wrap_f = Fernet(wrap_key)
        secret_f = Fernet(secret_key)
        wipe_f = Fernet(wipe_key)
        # Get the encrypted data by encrypting it with key the user will have and encrypting that
        # encrypted data with the wrap_key.
        secret_cipher = wrap_f.encrypt(secret_f.encrypt(secret_plain.encode('UTF-8'))).decode('UTF-8')
        wipe_cipher = wrap_f.encrypt(wipe_f.encrypt(wipe_plain.encode('UTF-8'))).decode('UTF-8')
        # Store the two tokens in the database with the secret_id as the Primary Key
        secret_id = self.database.create_secret_entry(secret_cipher, wipe_cipher, expire_in_seconds, is_consumable)
        secret_request_string = f"{secret_id}{secret_key.decode('UTF-8')}"
        wipe_request_string = f"{secret_id}{wipe_key.decode('UTF-8')}"
        return {
            # TODO: Figure out of returning Status is what we want to do, considering API Gateway vs Flask
            'status': 200,
            'secret_request_string': secret_request_string,
            'wipe_request_string': wipe_request_string
        }

    def get_secret(self, request_string):
        if len(request_string) != 76:
            # Request Strings are always UUIDs without dashes (32 char) + Fernet Generated Key (44 char) = 76 char
            # Figure out how to articulate errors later
            return {
                # Fix this status code to be correct
                'status': 404,
                'error': 'Malformed Request String'
            }
        secret_id = request_string[:32]
        encryption_key = request_string[32:]
        wrap_key = os.environ['PTS_WRAP_KEY'].encode('UTF-8')
        wrap_f = Fernet(wrap_key)
        decrypt_f = Fernet(encryption_key)
        secret_entry = self.database.retrieve_secret_entry(secret_id)
        # We're ALWAYS going to need to decrypt this one
        secret_entry['secret'] = secret_entry['secret'].encode('UTF-8')
        secret_decrypt_fail = False
        # Attempt to unwrap secret field
        try:
            unwrapped = wrap_f.decrypt(secret_entry['secret'])
        except InvalidToken:
            # If unsuccessful then the wrap_key has changed, return not found.
            # TODO: Should failures be logged somewhere which is not visible to users?
            return {'status': 404}
        # Attempt to decrypt secret field
        try:
            plaintext = decrypt_f.decrypt(unwrapped)
        except InvalidToken:
            # If decrypting secret with user-provided key is unsuccessful then set flag to try to decrypt wipe
            secret_decrypt_fail = True
        if secret_decrypt_fail == False:
            # If decrypting secret with user-provider key is successful return it
            return {
                'status': 200,
                'secret': plaintext.decode('UTF-8')
            }
        # If decrypting secret with user-provided key is unsuccessful then...
        # Attempt to unwrap wipe field
        try:
            unwrapped = wrap_f.decrypt(secret_entry['wipe'].encode('UTF-8'))
        except InvalidToken:
            # If unsuccessful then the wrap_key has changed, return not found.
            return {'status': 404}
        # If wipe unwrapping successful attempt to decrypt wipe field
        try:
            plaintext = decrypt_f.decrypt(unwrapped)
        except InvalidToken:
            # If decrypting wipe with user-provided key is unsuccessful then return not found.
            return {'status': 404}
        # If decrypting wipe with user-provider key is successful remove entry from the database
        # TODO: Do better parsing response and giving correct status code
        self.database.destroy_secret_entry(secret_id)
        return {'status': 200}
