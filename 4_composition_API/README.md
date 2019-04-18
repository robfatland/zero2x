# Composition API

## Introduction 


After the simple data query API is complete it is possible to make it more complicated. 
We recommend against the temptation to make 'one API to do everything': 
It can become complicated and brittle. We present here a second API that makes use
of the first. It calculates the speed and the dispersion of the congress of baboons
at a given time. 

## Design

Here there is no 'step 1' as the data are already available. In fact the Lambda function 
is created with an API Gateway per 'step 2' and populated with Python code that can be 
developed in a Jupyter notebook. 
