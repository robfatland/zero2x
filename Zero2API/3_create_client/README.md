# Create a Client for the API

## Introduction

Section `1_publish_table` placed data on the AWS cloud in a DynamoDB NoSQL database. Section `2_build_api` set up a basic
API for getting data subsets. It also set up an API supporting more complex calculations (moment of inertia). To take advantage
of these APIs within a Python program we now proceed to build Client code. Clients simply make API calls and receive data in
return. 

### baboons1 basic API Client code

This won't work at the moment as the API Gateway URL is obfuscated. 

```
# pandas library is used for talking with the baboons1 API
import pandas as pd

# use the 'baboons1' interface to get 11 rows of data

indiv = 10              # there are at least 38 GPS collars; we have here data for only 26 of them 
table = 'false'         # tabular data flag false means 'send the result as JSON'
t0 = '0:02:52'          # Time range begins at 2 minutes 52 seconds; duration 32 seconds
t1 = '0:03:24'          #   but only 22 seconds of data are returned

baseURL = 'https://xxxxxxxxxx.execute-api.us-west-2.amazonaws.com/default/baboon1'
url     = baseURL + '?indiv={}&table={}&t0={}&t1={}'.format(indiv,table,t0,t1)

a=pd.read_json(url)     # the url contains the details of the query; issued here
a                       # the response is a pandas DataFrame with 11 rows of data
```


### babooncomposition Client

This won't work at the moment as the API Gateway URL is obfuscated. 

```
import requests

# obtain one moment of inertia value for the entire troupe using one minute of data

urlcomp = 'https://yyyyyyyyyyy.execute-api.us-west-2.amazonaws.com/default/babooncomposition'
t0 = '11:00:00'
t1 = '11:01:00'
url= urlcomp + '?moi=true&t0={}&t1={}'.format(t0,t1)
a = requests.get(url)
print(a.content.decode('utf-8'))
```
