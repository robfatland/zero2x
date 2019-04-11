# Create a Client for the API

## Introduction

The API Client presented here is written in Python and uses pandas to send the query and work with the response. 

### Client code

```
import pandas as pd

indiv = 1
table = False
t0 = '0:02:52'
t1 = '0:03:52'

url= '[your_api_url]?indiv={}&table={}&t0={}&t1={}'.format(indiv,table,t0,t1)
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
