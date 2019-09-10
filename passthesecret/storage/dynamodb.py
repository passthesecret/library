import uuid
import datetime
import boto3
from botocore.exceptions import ClientError
import os


class DynamoDB(object):
    client = boto3.client('dynamodb')

    def create_secret_entry(self, secret_data, wipe_data, expire_in_seconds, is_consumable):
        # See MemoryDB implementation for extended explanation
        while True:
            secret_id = str(uuid.uuid4()).replace('-', '')
            # MemoryDB stores the timestamp in the form of a date on which it expires.
            expiration = (datetime.datetime.now() + datetime.timedelta(seconds=expire_in_seconds))
            try:
                response = self.client.put_item(
                    TableName=os.environ['PTS_DDB_SECRET_TABLE'],
                    Item={
                        'id': {'S': secret_id},
                        'secret': {'S': secret_data},
                        'wipe': {'S': wipe_data},
                        'expiration': {'N': str(int(expiration.timestamp()))},
                        'consumable': {'BOOL': is_consumable}
                    },
                    ConditionExpression='attribute_not_exists(id)'
                )
                return secret_id
            except ClientError as e:
                if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                    continue



    def retrieve_secret_entry(self, secret_id):
        # See MemoryDB implementation for extended explanation
        response = self.client.get_item(
            TableName=os.environ['PTS_DDB_SECRET_TABLE'],
            Key={
                'id': {'S': secret_id}
            }
        )
        if 'Item' in response:
            # The secret exists to retrieve it
            secret = {
                'id': response['Item']['id']['S'],
                'secret': response['Item']['secret']['S'],
                'wipe': response['Item']['wipe']['S'],
                'expiration': int(response['Item']['expiration']['N']),
                'consumable': response['Item']['consumable']['BOOL'],
            }
        else:
            # The secret doesn't exist so create a dummy one
            secret = {
                'id': secret_id,
                'secret': ('gAAAAABddtdvr6pSgtvGAsMVkH9aBvHlE1dFOH0UY1zcSlsFOYMxvzdCsTro'
                           'ma4iH2Qc2sU_mf2k9kpNGC7NQusw4tckpdmSYqgYexaRr4Bwe1rW9tFa98s='),
                'wipe': ('gAAAAABddtdv82xa6zoJwtgH0qmGCYtiqcCB6PNd8CozmTyYi6jQks5twksoYH1cbzxlG3'
                         'G5TePlkPEsiU8hymV-iPj1kcfz5tr0hUaHFUf8x6XWxRmrmxOh_m9HeCHyJO15SKqd50cz'),
                'expiration': 1568155243.205841,
                'consumable': False
            }
        # The secret (either real or dummy) should be checked for expiration
        if datetime.datetime.now() > datetime.datetime.fromtimestamp(secret['expiration']):
            # Expired so set a dummy secret
            secret = {
                'id': secret_id,
                'secret': ('gAAAAABddtdvr6pSgtvGAsMVkH9aBvHlE1dFOH0UY1zcSlsFOYMxvzdCsTro'
                           'ma4iH2Qc2sU_mf2k9kpNGC7NQusw4tckpdmSYqgYexaRr4Bwe1rW9tFa98s='),
                'wipe': ('gAAAAABddtdv82xa6zoJwtgH0qmGCYtiqcCB6PNd8CozmTyYi6jQks5twksoYH1cbzxlG3'
                         'G5TePlkPEsiU8hymV-iPj1kcfz5tr0hUaHFUf8x6XWxRmrmxOh_m9HeCHyJO15SKqd50cz'),
                'expiration': 1568155243.205841,
                'consumable': False
            }
        return secret

    def destroy_secret_entry(self, secret_id):
        response = self.client.delete_item(
            TableName=os.environ['PTS_DDB_SECRET_TABLE'],
            Key={
                'id': {'S': secret_id}
            },
            # Unfortunately we have to retrieve the record to verify deletion. If this is omitted delete_item() does
            # not give any indication that and item was deleted. With ReturnValues ALL_OLD the response contains the
            # items that were actually deleted.
            ReturnValues='ALL_OLD'
        )
        if 'Attributes' in response:
            return True
        else:
            return False
