## Usage
Before executing the dynmo_upload.py initial setup requires setting up requisite credential file for AWS.

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

## Lambda
AWS Lambda lets you run code without provisioning or managing servers and help building a serverless API.
lambda provides lightweight serverless way to serve an API. One downside is it doens't come with all python libraries except for the base packages and boto(Aws package). In order to use any other package we have to zip the package alongside our 'lambda_function.py' file for it to work.

In our case we need ```json2html``` so we need to zip ***json2html*** folder alongside the our ```lambda_function.py``` for it to work and uplaod it to lamdba.

Lets build the zip file for our lamdba function.

1) Create a temp folder to install all necessary packages. ```mkdir package```.

2) ```cd package```.

3) Install require packages in the temp folder created. ```pip install json2html --target``` .

4) Zip all the contents together. ```zip -r9 ../function.zip``` .

5) cd ../

6) Zip your custom python script to the already zipped packages. ```zip -g function.zip lambda_function.py```.

7)Upload the zip file ```function.zip``` in the lambda AWS UI.

This is how the UI of lambda would look like:
![lambda_ui](https://i.imgur.com/9KFK665.png)

This now has the required package json2html as folder which lambda can read from and our main module lambda_function.py

## Sample lamdba query
This is a sample lambda function that would serve as an api to query data for a baboon(indiv) between time intervals ```d0``` and ```dt```.

Params are:
 
- indiv=1 (to get baboons with id 1)
- table=true/false (whether to return a json or html formatted data)
- t0= start time ( time from which data required)
- t1= end time (time till which data should be queried)

*Sample API request: {your_api_url}?indiv=1&table=true&t0=0:02:52&t1=0:02:58*

Sample lamdba_function.py:
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
Or Use API endpoint using python

```
import pandas as pd

indiv = 1
table = False
t0 = '0:02:52'
t1 = '0:03:52'

url= '[your_api_url]indiv={}&table={}&t0={}&t1={}'.format(indiv,table,t0,t1)
pd.read_json(url)
```
