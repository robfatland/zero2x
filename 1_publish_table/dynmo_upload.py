

"""
    Utility script to load data into dynamodb.
"""

import os
from os.path import expanduser
import numpy as np
import pandas as pd

import boto3
from tqdm import tqdm
from multiprocessing import Pool
import json
import gc


def load_creds():
    """
        Utility function to read s3 credential file for
        data upload to s3 bucket.
    """
    home = expanduser("~")
    with open(os.path.join(home, 'creds.json')) as creds_file:
        creds_data = json.load(creds_file)
    return creds_data

def dynamodb_upload(data_frame):
    """
        Utility function to upload data to dynamodb
    """
    creds_data = load_creds()
    col_to_string = ['x', 'y', 'indiv'] #converting columns to string for DynamoDB
    for i in col_to_string:                                                                                                                        
        data_frame[i] = data_frame[i].astype(str)
    mydata=data_frame.T.to_dict().values() # converting dataframe to a dict for DynamoDB to consume
    resource = boto3.resource('dynamodb', aws_access_key_id=creds_data['key_id'],
         aws_secret_access_key=creds_data['key_access'], region_name='us-west-2')
    table = resource.Table('amboseli') # table name to push the data
    with table.batch_writer() as batch: # batch writer
        for row in tqdm(mydata):    #progress bar                                                                                                               
            batch.put_item(Item=row)


if __name__=='__main__':
    num_process = 10
    data = pd.read_csv('./baboons.csv') #S3 location of baboons dataset.
    split_df = np.array_split(data, num_process) # splitting data into  smaller data frames for each process.
    del data 
    gc.collect() # garbage collection to keep memeory usage in check.
    pool = Pool(processes = num_process)
    pool.map(dynamodb_upload, split_df)