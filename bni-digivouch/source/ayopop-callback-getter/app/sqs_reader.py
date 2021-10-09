import boto3
import os
import json, random, logging
from datetime import datetime
from string import Template
import time
import requests

logging.getLogger().setLevel(level=logging.DEBUG)

sqs = boto3.client('sqs')
queue_url = os.getenv('SQS_URL', 'https://sqs.ap-southeast-2.amazonaws.com/395824552236/q-ayopop-dev')

def get_from_queue(queue_url):
    # print(resp)
    # Receive message from SQS queue
    while True:
        response = sqs.receive_message(
            QueueUrl=queue_url,
            AttributeNames=[
                'SentTimestamp'
            ],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
            ],
            VisibilityTimeout=0,
            WaitTimeSeconds=10
        )
        try:
            yield from response['Messages']
        except KeyError:
            return 
       
        message = response['Messages'][0]
        receipt_handle = message['ReceiptHandle']

        # Delete received message from queue
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        print('Received and deleted message: %s' % message)

if __name__ == '__main__':
   for message in get_from_queue(queue_url):
       print(json.dumps(message))

       # Configure json indexes
       a = json.loads(message["Body"])
       b = json.loads(a["body"])
       c = json.loads(json.dumps(b))
       d = c["data"]
       e = c["message"]

       trx_id = d.get("transactionId")
       account_num = d.get("accountNumber")
       product_code = d.get("productCode")
       ref_num = d.get("refNumber")
       amount = d.get("amount")
       response_code = c["responseCode"]
       response_message = e.get("ID")

       save_to_db = {
               "transaction_id" : trx_id,
               "callback_date" : "2021-09-08T00:46:47.129Z",
               "account_num_voucher": account_num,
               "product_code": product_code,
               "ref_number": ref_num,
               "amount": amount,
               "response_code": response_code,
               "response_message": response_message  
               }

       dbsave = json.dumps(save_to_db)

       save_request = requests.post("http://database-write:8000/db/callback", json=json.loads(dbsave))
       print(save_request.json())


    # trx_id = message["body"][""]
    # account_num = message["body"][""]
    # product_code = message["body"][""]
    # ref_num = message["body"][""]
    # amount = message["body"][""]
    # response_code = message["body"][""]
    # response_message = message["body"][""]

    # save_to_db = {
    #         "transaction_id" : trx_id,
    #         "account_num_voucher": account_num,
    #         "product_code": product_code,
    #         "ref_number": ref_num,
    #         "amount": product_code,
    #         "response_code": response_code,
    #         "response_message": response_message  
    #         }

    # dbsave = json.dumps(save_to_db)

    # save_request = requests.post("http://database-write:8000/db/statusupdate", json=json.loads(dbsave))
    # print(save_request.json())

# def get_from_queue(queue_url):
#    # Receive message from SQS queue
#    while True:
       
#        response = sqs.receive_message(
#            QueueUrl=queue_url,
#            AttributeNames=[
#                'SentTimestamp'
#            ],
#            MaxNumberOfMessages=1,
#            MessageAttributeNames=[
#                'All'
#            ],
#            VisibilityTimeout=0,
#            WaitTimeSeconds=10
#        )
#        try: 
#            yield from response['Messages']
#        except KeyError:
#            return 
       
#        message = response['Messages'][0]
#        receipt_handle = message['ReceiptHandle']
#        # Delete received message from queue
#        sqs.delete_message(
#            QueueUrl=queue_url,
#            ReceiptHandle=receipt_handle
#        )
#        print('Received and deleted message: %s' % message)

# if __name__ == '__main__':
#    for message in get_from_queue(queue_url):
#        print(json.dumps(message))

