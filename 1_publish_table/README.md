# Publishing your data table on the cloud

## Introduction


**1_publish_table** is your first step, pushing a tabular dataset onto the AWS DynamoDB NoSQL database. 
Step 2 will be to add programmatic access 
(an Application Programming Interface or 
[API](https://en.wikipedia.org/wiki/Application_programming_interface)) to this table.


Provided as an example is a tabular dataset as CSV file called  `baboons.csv`.
This is 1048576 rows including one header row: In four columns `indiv, time, x, y`.

You will need an AWS account where you feel comfortable logging in, managing and monitoring your spend, 
and following appropriate security guidelines concerning IAM Users and access keys. If this is not 
familiar we discourage you from going further with this tutorial until you can check that box. 


[DynamoDB](https://en.wikipedia.org/wiki/Amazon_DynamoDB) is populated with tables. We prepare
the table in advance and then upload the `.csv` file to that table. We then record the table's
resource address for subsequent steps.


The data may be in a local file (as in this example) or elsewhere, as in AWS S3 object storage. 


flag
![Zero to API](https://i.imgur.com/qiCcCNL.jpg)


Our example data is as noted a CSV table of baboon positions -- in meters -- for 25 individuals located
at the [Amboseli Baboon Research Project](https://en.wikipedia.org/wiki/Amboseli_Baboon_Research_Project)
site in Kenya. We use `boto3`, a Python library for AWS interactions. 

## Procedure outline (all three steps)


Note that '**Your machine**' might be an AWS EC2 instance or some other cloud instance, say on GCP or Azure.
You might also be interested in using a Jupyter notebook as your working environment. 


- 1_publish_table step
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

- 2_build_api step

- **Your machine** Prepare Lambda function code as a zip file
- **AWS Console** Create the Lambda API powered by the zip file from the previous step
  - This Lambda function will access the DynamoDB table created above
- **AWS Console** Associate an API Gateway with this lambda function
  - This can also be done from your machine using the AWS CLI
  
- 3_create_client step
  - **Your machine** configure a client to request data
  - **Your machine** Test the interface


## Procedure for 1_publish_table

### Prepare your tabular data file

Your `.csv` table should be free of extraneous delimiters and should be complete.
We recommend filling holes with a no-data marker of some kind. 

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

DynamoDB data are read from a table as a dictionary.
DynamoDB tables have two attributes:


    1) A Partition Key - For this case we use the 'indiv' column
    2) A Sort Key - Here we use 'time' (this is optional)
        
These tables may have further columns that are not keys as such. 
The Partition Key gives a first data subdivision. It supports strict equality in queries.
The Sort Key gives a second queryable attribute. This supports ranges or inequalities.
The Sort Key is optional and can improve query time. 

DynamoDB allows queries against Partition Key and Sort Key. There is a second type of 'query' 
supported by DynamoDB called a **scan**. The scan operation is slower. This suggests using Python
timing tools with the API client to resolve 'how much slower?' 

Our `baboons.csv` data has columns **indiv, time, x, y**. Set the Partition Key to be 'indiv'
and the Sort Key to be 'time'. 

DynamoDB sets read and write limits at 5 hits by default. When uploading data we temporarily 
increase the write limit to speed up the writing process.  

![Baboons Table](https://imgur.com/kzDXUvq.png)

> Interface screenshot

![Table keys](https://imgur.com/dGm5Kvh.png)

> Interface screenshot

![DaynamoDB](https://i.imgur.com/EzC3t8R.png)

> Interface screenshot

Once the table is **Created**...

- We proceed to upload data to it
  - This is done using a parallel batch approach to speed up the process
- We then set the write limit back to 5 to save money

### Upload data to the DynamoDB table

Modify the 
