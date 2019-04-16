# 2_build_api 


## Introduction

This step provides access to the data table published in part 1 via internet query and response. 
This transaction uses a browser for manual testing or Python code (see part 3). For example if you paste 
the following into a browser address bar:

```
https://rlu4ch9a57.execute-api.us-west-2.amazonaws.com/default/baboon1?indiv=10&table=true&t0=9:00:00&t1=9:00:22
```

...you should see a small data table after a few seconds. This is 22 seconds of position fixes for *individual 10*
where *individual 10* would resemble the animal wearing the GPS collar in this photograph:


<img src="https://github.com/robfatland/Zero2API/blob/master/2_build_api/baboons.png" alt="Amboseli baboons" width="550"/>



## Lambda function API


This section describes installing the table interface using an AWS Lambda function. 
For our purposes: A Lambda function is Python code that runs in response to some *trigger*;
here a web query.  


### A note on Python for Lambda functions


Python code often depends upon locally-installed libraries bundled as 'packages'. AWS Lambda supports some
basic packages as well as the AWS interface Python package called `boto3`. If other packages are needed they 
must be bundled up locally and imported into the Lambda configuration environment on the AWS cloud as zip files. 
In Zero2API we use `json2html` package and so we create a bundle containing that package. See 
[this link](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html#python-package-dependencies)
for more on Python deployment packages for AWS Lambda.

#### `json2html` inclusion in a (Python) Lambda function


- Create a file called `lambda_function.py` in some Linux working directory. 
  - If you are running Windows you will first need to install a 
  [**bash shell/environment**](https://www.windowscentral.com/how-install-bash-shell-command-line-windows-10).
  - The contents of the file `lambda_function.py` are immaterial at this point; here is why:
    - Eventually this file will contain Python code for the API
    - It can be edited through the AWS console as we refine and debug this API
    - Therefore for the moment the file contents can be placeholder text like `xyz`
- Noting the period characters '.' in what follows: From the directory containing `lambda_function.py` issue:

```
$ mkdir package
$ cd package
$ pip install json2html --target .
$ zip -r9 ../function.zip .
$ cd ../
$ zip -g function.zip lambda_function.py
```

The first `zip` command creates a zip file `function.zip` containing the code for the `json2html` package. 
The second `zip` command adds the `lambda_function.py` code to this zip file. The resulting zip file should
unbundle properly within the AWS Console interface.


#### Create the Lambda function on the AWS console

The next step is to transfer the zip file from the previous step to the Amazon cloud and construct the associated Zero2API 
Lambda function as follows: 


- Sign in to the AWS console and follow these procedural steps
  - Create an IAM Role called `zero2api` and attach these managed policies:
    - AmazonAPIGatewayInvokeFullAccess (connect Lambda to the API Gateway service)
    - AmazonDynamoDBReadOnlyAccess     (connect Lambda to the DynamoDB database)
    - CloudWatchFullAccess             (enable Lambda to write to CloudWatch logs; useful for debugging)
  - Create a Lambda function
    - Python 3.7 
    - Assigned the `zero2api` role from the previous step
    - In the **Function Code** interface: Upload `function.zip` from above, **Save**
      - The zip file should unpack and be visible in the **Function Code** area of the Lambda **Configuration** tab
      - The file `lambda_function.py` can now be further edited
        - Edits only modify the AWS copy of course, not your original file
        - Alternatively you can modify, re-zip and re-upload your code
          - This is slower but keeps local code identical to your AWS code
    - Add **Environment Variables**
      - This detail should in principle be deleted; but (flag) this needs to be tested
      - In the **Environment Variables** section create **AKEY** and **SKEY**
        - You give these two keys *values* taken from an AWS access key that you generate separately
          - AKEY is the Access Key and SKEY is the Secret Key
          - Anyone with these keys can use your account
          - It is vital that you not place these keys in a public location such as GitHub
            - Why? Without any exaggeration: Nefarious individuals will appropriate such keys for their personal gain
            - We have seen firsthand such individuals use access keys to mine bitcoin at a cost of tens of thousands of dollars 
            - Therefore: Use extreme caution in managing access keys
    - Under **Basic Settings** set the timeout to 5 minutes and the memory to 256MB
    - In the **Designer** interface (top of the **Configuration** page) add API Gateway (left side) as a Lambda trigger
      - Click on the API Gateway rectangle to activate and configure it (below **Designer**)
        - Create a new API
        - Security: Set as **Open** or as desired  
        - Deployment stage: Default
        - **Add** button, lower right
    - **Save** the Lambda function
      - Note the resulting API Gateway endpoint URL
        - This URL is the basis for API call; see see next section `3_create_client`


This is how the Lambda Function Code section appears:


![lambda_ui](https://i.imgur.com/9KFK665.png)


### Template for `lambda_function.py`


The `lambda_function.py` file will run in response to a web query passed in the form of a query string appended to a 
base URL. The Lambda function will interpret this string to formulate a query that is applied to the DynamoDB table
published in step 1. The results of this query are then bundled either as HTML or JSON and returned to the calling 
entity.


Here is example code for the `lambda_function.py` file.


```
import json, boto3, os
from boto3.dynamodb.conditions import Key, Attr
from json2html import *
from datetime import date, datetime, time, timedelta

ACCESS_KEY_ID, SECRET_ACCESS_KEY = os.environ['AKEY'], os.environ['SKEY']

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=ACCESS_KEY_ID, 
                 aws_secret_access_key=SECRET_ACCESS_KEY, region_name='us-west-2')
    table    = dynamodb.Table('baboons1')
    baboon   = str(event["queryStringParameters"]['indiv'])
    t0       = str(event["queryStringParameters"]['t0'])
    t1       = str(event["queryStringParameters"]['t1'])
    dfflag   = event["queryStringParameters"]['table'].lower() == "true"
    response = table.query(KeyConditionExpression=Key('indiv').eq(baboon) & Key('time').between(t0, t1))

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


### query versus scan

