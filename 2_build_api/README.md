# 2_build_api 

## Introduction

Upon completing this step you will be able to retrieve data from your DynamoDB-stored table either directly 
using a URL (say in your browser) or programmatically (say from a Python client). An example request will look
like this: 

```
{your_api_url}?indiv=10&table=true&t0=0:20:00&t1=0:30:00
```

This will retrieve ten minutes of position fixes for one individual in table (rather than JSON) format.
Since the fixes occur once every two seconds this will be about 300 values.


flag left off here


Note: - In your custom lambda function add API Gateway with your required configuration and this would yeild {your_api_url}.

### Lambda function API

flag

AWS Lambda functions run code (Python in our case) without provisioning or managing an actual
computer; or 'server'; or 'Virtual Machine'. The result is a *serverless API*.
(There really is a computer / server / Virtual Machine involved; we just never see it or think about it.) 


Lambda functions are lightweight abstractions that simplify getting executable code running as a service.
They do not typically come with all conceivable Python libraries available; just some commonly used base 
packages plus `boto3`, the AWS interface package. To use other packages that are not available by default
we must zip up a computing environment that contains our Python lambda code 'lambda_function.py' together
with the package libraries we want to use.


In this case we operate on JSON-format text and so need `json2html`.  We therefore include the `json2html` folder 
within our working folder together with `lambda_function.py`. The zip file is uploaded to the AWS cloud as a 
Lambda function bundle. 


Let's build this zip file.

- Create a temp folder `package` where we will install everything necessary. 

```
$ mkdir package
$ cd package
$ pip install json2html --target .
```

- Zip the contents; then zip your lambda function code together with that 

```
$ zip -r9 ../function.zip
$ cd ../
$ zip -g function.zip lambda_function.py
```

- Using the AWS Console: Upload `function.zip` to an AWS Lambda function

This is how the UI of lambda would look like:

![lambda_ui](https://i.imgur.com/9KFK665.png)

This has the necessary `json2html` folder which Lambda will read from our main module lambda_function.py

### lambda_function.py


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
    # response = table.scan(FilterExpression=Key('indiv').eq(baboon) & Key('x').between(d0, final_dt.strftime("%T")))

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


#### Test: A sample lamdba query

This is a sample lambda function that would serve as an api to query data for a baboon(indiv) between time intervals ```d0``` and ```dt```.

Params are:
 
- indiv=1 (to get baboons with id 1)
- table=true/false (whether to return a json or html formatted data)
- t0= start time ( time from which data required)
- t1= end time (time till which data should be queried)
