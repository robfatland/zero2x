# 2_build_api 

## Introduction

This step creates URL-based query access to the data table published in part 1. This access can be done 
using a URL (say in your browser) or programmatically from a Python client. An example query will look
like this: 

```
{your_api_url}?indiv=10&table=true&t0=0:20:00&t1=0:30:00
```

This will retrieve ten minutes of position fixes for one individual in table format (not JSON).
Since the fixes occur once every two seconds this will be about 300 values.


flag refine this


In your custom lambda function add API Gateway with your required configuration and this would yeild {your_api_url}.


## Lambda function API

flag

AWS Lambda functions run code (Python in our case) without provisioning or managing an actual
computer (Virtual Machine). There *is* a computer involved but we never see this.


Python often uses packages that are custom-installed locally. On AWS Lambda the Python environment
has some basic packages available; but not all possible Python libraries are pre-installed. (The `boto3` 
package *is* preinstalled to provide Python access to AWS.) To use other packages that are not available 
by default we zip up a computing environment containing both our Python Lambda code (the file is called
`lambda_function.py` together with package libraries we want to use.


In our Zero2API case we operate on JSON-format text and so need the `json2html` package.  
We build a zip file using two `zip` commands. The first zips the package folder recursively and
the second adds the API code in `lambda_function.py`. See 
[this link](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html#python-package-dependencies)
for more on Python deployment packages for AWS Lambda.

- Create the `lambda_function.py` file in some directory on a Linux system
  - See template file given below
- From this same location (being sure to include the periods) issue:

```
$ mkdir package
$ cd package
$ pip install json2html --target .
$ zip -r9 ../function.zip .
$ cd ../
$ zip -g function.zip lambda_function.py
```

The first `zip` command creates a zip file `function.zip`. The second `zip` command adds the lambda function 
code to this zip file. 


- Log in to the AWS console 
  - Create a role named (say) `zero2api` with two attached policies
    - AmazonAPIGatewayInvokeFullAccess
    - AmazonDynamoDBReadOnlyAccess
  - Also on the console: Create a Lambda function
    - Specify Python 3.7 
    - Assign the Lambda the `zero2api` role
    - Upload `function.zip` as the code base
      - This is un-packed and shown in the Function Code section of the Lambda configuration page
    - Add environment variables AKEY and SKEY with values taken from an AWS access key
      - AKEY is the Access Key
      - SKEY is the Secret Key
    - In the Designer add an API Gateway (left side) as a trigger for this Lambda function
      - Click on this to configure it
        - Create a new API
        - Open Security
        - Deployment stage: Default
        - Click 'Add' at the lower right
      - Once configured note the API Gateway endpoint information
        - API, endpoint URL and name: All listed in the Lambda      


flag we should be able to do this with just roles, not access keys...


This is how the Lambda Function Code section appears:


![lambda_ui](https://i.imgur.com/9KFK665.png)


This has the necessary `json2html` folder which Lambda will read from our main module lambda_function.py


### Template for `lambda_function.py`


```
import json
from boto3.dynamodb.conditions import Key, Attr
import boto3
from json2html import *
from datetime import date, datetime, time, timedelta

import os
SECRET_ACCESS_KEY = os.environ['SKEY']
ACCESS_KEY_ID = os.environ['AKEY']

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', \
               aws_access_key_id=ACCESS_KEY_ID, \
               aws_secret_access_key=SECRET_ACCESS_KEY, \
               region_name='us-east-1')
    table    = dynamodb.Table('baboons')
    baboon   = str(event["queryStringParameters"]['indiv'])
    t0       = str(event["queryStringParameters"]['t0'])
    t1       = str(event["queryStringParameters"]['t1'])
    dfflag   = event["queryStringParameters"]['table'].lower() == "true"
    
    response = table.query(KeyConditionExpression=Key('indiv').eq(baboon) & Key('time').between(t0, t1))

    for item in response['Items']: item['row'] = float(item['row'])

    # response = table.query(KeyConditionExpression=Key('indiv').eq(baboon) & Key('time').between(d0, final_dt.strftime("%T")))
    # response = table.scan(FilterExpression=Key('indiv').eq(baboon) & Key('x').between(d0, final_dt.strftime("%T")))

    if not dfflag:
        print("Returning JSON")
        dict_string = json.dumps(response['Items'], indent=4)
        return { "statusCode": 200, "body": dict_string }
    else:
        print("Returning HTML")
        return { 
            "statusCode": 200, 
            "body": json2html.convert(response['Items']),  
            "headers": {'Content-Type': 'text/html'}
        }
```

### Sample Client code

```
import pandas as pd

indiv = 1
table = False
t0 = '0:02:52'
t1 = '0:03:52'

url= '[your_api_url]indiv={}&table={}&t0={}&t1={}'.format(indiv,table,t0,t1)
pd.read_json(url)
```


### Test: A sample lamdba query

This is a sample Lambda function that would serve as an api to query data for a baboon(indiv) between 
times intervals ```t0``` and ```t1```.

Params are:
 
- indiv=1 (to get baboons with id 1)
- table=true/false (whether to return a json or html formatted data)
- t0= start time ( time from which data required)
- t1= end time (time till which data should be queried)
