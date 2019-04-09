# Publishing a data table to the cloud

## With supporting API

### Introduction


This publish_table README walks you through publishing a tabular dataset. 

flag
and connecting programmatic access 
(an Application Programming Interface or [API](https://en.wikipedia.org/wiki/Application_programming_interface)) to that data.

Provided is a tabular dataset as a CSV file: 1048576 rows including one header row and four columns.

flag
in a text file and we proceed on the
[Amazon public cloud](http://aws.amazon.com). 

You will need an AWS account where you feel comfortable logging in, managing and monitoring your spend, and following
appropriate security guidelines concerning IAM Users and access keys. 

flag
warning ref needed 
to the console and tracking your spend so that you do not exceed your
budget. 


Here we use a NoSQL database service on AWS called DynamoDB.  

- configure a table within DynamoDB
- load the tabular data
- record the resource address

flag 
and then configure the API using two additional AWS services: Lambda
serverless compute service and the AWS API Gateway. You may also use AWS S3 object storage to stage
the tabular data for loading if you like. 

flag
![Zero to API](https://i.imgur.com/qiCcCNL.jpg)


flag left off here decomposition phase

Our example data is as noted a CSV table of baboon positions -- in meters -- as measured by a set individuals located
at the [Amboseli Baboon Research Project](https://en.wikipedia.org/wiki/Amboseli_Baboon_Research_Project)
site in Kenya. This procedure can be done from a laptop where Python and the `boto3` package have been
pre-installed. `boto3` is a library for talking to the Amazon cloud. Here is the procedure outline.


- **Your machine** Configure and clean up a tabular .csv file
  - store it on your local computer
  - or stage it to AWS S3 object storage (you will need the URL and the CSV file must be public)
- **Your machine** Configure a credentials file
- **Your machine** Ensure Python and necessary packages are installed
  - Particularly { boto3, numpy, pandas, tqdm } and any dependencies
- **AWS Console** Set up a DynamoDB RDS
  - Create an empty table and configure write speed for loading
- **Your machine** Load the data to this DynamoDB table using `dynamo_upload.py` provided here
- **AWS Console** Verify the data loaded into DynamoDB and reset the write speed for cost management
- **Your machine** Prepare Lambda function code as a zip file
- **AWS Console** Create the Lambda API powered by the zip file from the previous step
  - This Lambda function will access the DynamoDB table created above
- **AWS Console** Associate an API Gateway with this lambda function
  - This can also be done from your machine using the AWS CLI
- **Your machine** Test the interface


### Prepare your tabular data file


### Configure AWS credentials

Before uploading your tabular data file (by executing the `dynmo_upload.py` script provided here)
you will need to create an AWS credentials file. The file looks like this: 


```{"key_id": "ABCDEFGHIJKLMNOPQRST", "key_access": "+4silQghzOLlflsUJ7PRdldx5QQ60kdakRslkgjF"}```


You can simply copy/paste this template and replace the two values with the correct values for a working
access key. You generate a key at the AWS Console under the `IAM` service, associated with your IAM User account.
Once you have the key you can also using the following Python script to generate a properly formatted 
credential file. You will need to insert the `id` and `access` strings in this script; then run it once; 
and then delete the script. The credentials will be stored in your home folder as `creds.json`. 


> ***IMPORTANT: Do not store your credentials or your credential-generator script in a GitHub repository.
If you do so you are subject to account abuse by malicious bots that scan GitHub across versions for usable
keys. Failing to follow this guideline can be disastrous.***

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


### Ensure Python and necessary packages are installed

You can for example proceed on a Windows laptop where `bash` is installed; or on a Linux 
machine where `bash` is the default shell program (operating system interface language).


- `$ wget https://repo.continuum.io/miniconda/Minconda3-latest-Linux-x86_64.sh`
- `$ bash Minconda3-latest-Linux-x86_64.sh` + agreeable responses to prompts
- `$ source ~/.bashrc` to activate the `conda` command
- `$ conda install numpy` and so on for pandas, tqdm, boto3; again being agreeable
- `$ pip freeze` to list installed packages
- `$ pip freeze > requirements.txt` to create an environment file

You are not required to generate the `requirements.txt` file. We mention this in passing as
a useful technique for automation tasks that will come up in related work. 


With the above steps completed: Create a file `go.py` consisting of this text:

```
import boto3
import numpy as np
import pandas as pd
import tqdm

print('words words words...')
```

This should run properly without errors when you type in

```
$ python go.py
```


### Create a DynamoDB table

Amazon DynamoDB is a non-relational database. Data is read as a dictionary.
DynamoDB works with tables that have two attributes:


    1) A Partition Key - For this case we use the 'indiv' column
    2) A Sort Key - Here we use 'time' (this is optional)
        
The Partition Key gives us a first data subdivision that maps to strict equality in queries.
The Sort Key gives us a second queryable attribute; and here we can query by range / inequality.
The sort key is optional but can improve query time if the column is likely to be queried by the Researcher. 


DynamoDB only allows queries against Partition and Sort keys, i.e. columns in your data table. 
One may not query other columns but the *scan* operation amounts to the same thing (search based
on column values) albeit slower. 


### Example from the Amboseli data: indiv, time, x, y

Our data has columns ['time','x', 'y', 'indiv'] filtering and subsetting can only be done on our Partition key('indiv')
and sort key('time') and not on either 'x' or 'y', so a query to fetch all 'x' == 728.2 won't work.

DynamoDB sets read and write limit which are both defaulted to 5 hits. This can be increase or decreased based on API requirement.
Following is a screenshot of the UI for DynmoDB

![Baboons Table](https://imgur.com/kzDXUvq.png)

Then provide appropriate Keys to the table.

![Table keys](https://imgur.com/dGm5Kvh.png)


### Uploading Data from S3 to Dynamodb

#### Configuring the read and write speed in the DynamoDB UI.

Once done creating a [DynamoDB](https://aws.amazon.com/dynamodb/) table using the GUI on AWS, next step involves reading the csv from S3 bucket(Public Url) or files present locally to this newly created table.

For the data upload since the default write limit(5) would be low for 1 million rows to be transferred we'll increase this number to 1000 on the DynamoDB GUI ![DaynamoDB](https://i.imgur.com/EzC3t8R.png)

We have created a table called 'baboons' with Partition Key = 'indiv' and Sort Key = 'time

Once done trasnferring write capacity units should be set back to lower values for lesser cost(default =5).

Since we have a million rows to process we will subset out data files into small chunks(10 for this example) and batch process them to make upload faster.

The run time for this would be around 15mins, without multiprocesing it would around 150mins.


### Lambda function API


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

*Sample API request: {your_api_url}?indiv=1&table=true&t0=0:02:52&t1=0:02:58*

Note: - In your custom lambda function add API Gateway with your required configuration and this would yeild {your_api_url}.
