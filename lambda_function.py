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
                   aws_access_key_id=ACCESS_KEY_ID, 
                   aws_secret_access_key=SECRET_ACCESS_KEY, 
                   region_name='us-west-2')
    table    = dynamodb.Table('baboons1')
    baboon   = str(event["queryStringParameters"]['indiv'])
    t0       = str(event["queryStringParameters"]['t0'])
    t1       = str(event["queryStringParameters"]['t1'])
    dfflag   = event["queryStringParameters"]['table'].lower() == "true"

    # two query types: query and scan; here are format notes: 
    #   response = table.query(KeyConditionExpression=Key('indiv').eq(baboon) & Key('time').between(d0, final_dt.strftime("%T")))
    #   response = table.scan(FilterExpression=Key('indiv').eq(baboon) & Key('x').between(d0, final_dt.strftime("%T")))

    response = table.query(KeyConditionExpression=Key('indiv').eq(baboon) & Key('time').between(t0, t1))

    for item in response['Items']: item['row'] = float(item['row'])

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
