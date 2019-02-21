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

## Runtime

For the data upload since the default write limit(5) would be low for 1 million rows to be transferred we'll increase
this number to 1000 in the DynamoDB GUI.
Since we have a million rows to process we will subset our data files into small chunks(10 for this example) and batch process them to make upload faster.

The run time for this setup is around **15mins**.

## Sample lamdba query
This is a sample lambda function that would serve as an api to query data for a baboon(indiv) between time intervals 'd0' and 'dt'.

Params are:
 
- indiv=1 (to get baboons with id 1)
- table=true/false (whether to return a json or html formatted data)
- d0= start time ( time from which data required)
- dt= end time (time till which data should be queried)

*Sample API request: {your_api_url}?indiv=1&table=true&d0=0:02:52&dt=0:02:58*

Sample lamdba_function:
```
import json
from boto3.dynamodb.conditions import Key, Attr
import boto3
#from pprint import pformat
from json2html import *
from datetime import date, datetime, time, timedelta

import os
SECRET_ACCESS_KEY = os.environ['SKEY']
ACCESS_KEY_ID = os.environ['AKEY']

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=ACCESS_KEY_ID, aws_secret_access_key=SECRET_ACCESS_KEY, region_name='us-east-1')
    table = dynamodb.Table('baboons')
    baboon = str(event["queryStringParameters"]['indiv'])
    t0 = str(event["queryStringParameters"]['t0'])
    t1 = str(event["queryStringParameters"]['t1'])
    data_frame_flag = event["queryStringParameters"]['table'].lower() == "true"

    # This was a look into time-zero t0 and delta-time dt but abandoned because data were inconsistent
    # initial_t0 = time(*map(int, t0.split(":")))
    # final_t1 = (datetime.combine(date.today(), initial_t0) + timedelta(minutes=int(dt))).time()
    
    response = table.query(KeyConditionExpression=Key('indiv').eq(baboon) & Key('time').between(t0, t1))

    for item in response['Items']:
        item['row'] = float(item['row'])

    # response = table.query(KeyConditionExpression=Key('indiv').eq(baboon) & Key('time').between(d0, final_dt.strftime("%T")))

    if not data_frame_flag:
        print("Returning JSON")
        dict_string = json.dumps(response['Items'], indent=4)
        return { "statusCode": 200, "body": dict_string }
    else:
        print("Returning HTML")
        return { 
            "statusCode": 200, 
            "body": json2html.convert(response['Items']),  
            "headers": {
        'Content-Type': 'text/html'
    }}


```
