class Manager(object):

    def create_secret(self, secret, expire_in_seconds, burn_after_reading):
        return {
            'view_request_string': 'SomeCode',
            'wipe_request_string': 'SomeCode'
        }
