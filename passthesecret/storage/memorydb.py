import uuid


class MemoryDB(object):
    secret_table = {}

    def create_secret_entry(self, secret_data, wipe_data, expiration, consumable):
        # Prevent duplicate entries:
        #    MemoryDB - Have to check if key exists first
        #    DynamoDB - Use put_item's attribute_not_exists
        #    Redis - Use SETNX (SET if Not eXists)
        # Basically attempt to insert, let the DB engine fail, retry until you get a successful insert with a new ID
        # Since we're using UUIDs this should literally never happen, but we don't EVER want to accidentally overwrite
        # existing good data. This method allows us to not take a check-before-write cycle and let the checking happen
        # during insert and only submitting two queries if we have to anyway.
        while True:
            secret_id = str(uuid.uuid4()).replace('-', '')
            if secret_id in self.secret_table:
                continue
            self.secret_table[secret_id] = {
                'id': secret_id,
                'secret': secret_data,
                'wipe': wipe_data,
                'expiration': expiration.timestamp(),
                'consumable': consumable

            }
            return secret_id

    def retrieve_secret_entry(self, secret_id):
        return self.secret_table[secret_id]
