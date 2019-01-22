## Usage
Before executing the dynmo_upload.py initial setup requires setting up requisite credential file for AWS S3.

Provide one time key_id and key_access to be stored in the home folder as creds.json which will be used by dynmo_upload.py.

```
import os
from os.path import expanduser

home = expanduser("~")
# store one time credentials in the home directory
creds = {'key_id' : '',
         'key_access' : ''}
with open(os.path.join(home,'creds.json'), 'a') as cred:
    json.dump(creds, cred)
```

## Sample lamdba query
This is a sample lambda function that would serve as an api to query data for a baboon(indiv) between time intervals 'd0' and 'dt'.
```
import json
from boto3.dynamodb.conditions import Key, Attr
import boto3
from pprint import pformat
from json2html import *

MY_SECRET_ACCESS_KEY = '' 
MY_ACCESS_KEY_ID = ''

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=MY_ACCESS_KEY_ID, aws_secret_access_key=MY_SECRET_ACCESS_KEY, region_name='us-east-1')
    table = dynamodb.Table('baboons')
    baboon = str(event["queryStringParameters"]['indiv']) # parse api call to get indiv
    d0 = str(event["queryStringParameters"]['d0']) # parse api call to get start time
    dt = str(event["queryStringParameters"]['dt']) # parse api call to get end time
    data_frame_flag = event["queryStringParameters"]['table'].lower() == "true" # parse api call to get table flag
    # query dynamoDB for the parsed filter parameters and return a response.
    response = table.query(KeyConditionExpression=Key('indiv').eq(baboon) & Key('time').between(d0, dt))

    dict_string = pformat(response['Items']) #prettify the dict for asthetics
    #conditional return a html table based on table flag in the api call.
    if not data_frame_flag:
        print("Returning JSON")
        return { "statusCode": 200, "body": dict_string }
    else:
        print("Returning HTML")
        return { 
            "statusCode": 200, 
            "body": json2html.convert(response['Items']),  
            "headers": {
        'Content-Type': 'text/html',
    }}

```
