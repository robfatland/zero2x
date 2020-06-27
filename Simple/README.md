# Simple example

Let's build a prime factorization service as a Lambda function on AWS. 

- Get an account, sign in to the AWS Management Console
- Navigate to AWS Services > Lambda, click Create Function
- Follow the steps in the photo guide at the bottom of this page. I give them here in outline:
  - Create a new Lambda function; give it a name, choose Python 3
  - Create an Execution role: Use the defaults to get a basic execution policy: allows the Lambda to run
  - Add an API Gateway to trigger the Lambda function, note the endpoint this generates
  - Copy the Python code below into the code editor
  - Copy the endpoint URL from above, append `?n=2020`:  In a browser address bar
    - This should return a text string in your browser: The prime factorization of 2020
  
```
# From Zero2API / Simple on GitHub
# In browser: https://kep5pu8n09.execute-api.us-west-2.amazonaws.com/default/primefactors?n=4700

import json

def lambda_handler(event, context):
    return_msg, n0 = '', int(event["queryStringParameters"]['n'])

    if n0 < 2:
        n0 = 103598728
        return_msg += 'Could not parse input; using n = '

    return_msg += str(n0) + ' = '
    prime_factors, factor_candidate, n = [], 2, n0
    while factor_candidate ** 2 <= n:
        if n % factor_candidate:
            if factor_candidate == 2: factor_candidate = 3
            else:                     factor_candidate += 2
        else:
            n = n / factor_candidate
            prime_factors.append(factor_candidate)
    if n > 1: prime_factors.append(n)
        
    npf = len(prime_factors)
    for i in range(npf - 1): return_msg += str(prime_factors[i]) + ' * '
    return_msg += str(int(prime_factors[npf - 1]))
    return { "statusCode": 200, "body": return_msg }
```

Here is an unrelated and more complicated program for a middle school coding challenge called "dronebees".

```
# debug: include 'print(d)' and use the Monitoring tab to find/read the log
import json
import os
from random import uniform
from math import exp, floor, sqrt

# this is a bit hard-coded
nHives = 3
baseDensity = 2.
uniformLow = 0.
uniformHigh = 7.

c = [(float(os.environ['x0']), float(os.environ['y0']), float(os.environ['z0']))]
c.append((float(os.environ['x1']), float(os.environ['y1']), float(os.environ['z1'])))
c.append((float(os.environ['x2']), float(os.environ['y2']), float(os.environ['z2'])))
sigma = (float(os.environ['sigma_x']), float(os.environ['sigma_y']), float(os.environ['sigma_z']))

def lambda_handler(event, context):
    if event.get('queryStringParameters') == None:
        return { "statusCode": 200, "body": 'add ?x=4.&y=3.&z=1 to request (any x/y/z coordinates are fine)'}
    rs = ''
    d = event['queryStringParameters']
    # determine if this is a request for 'hard' mode (narrower spikes)
    verbose = False
    if d.get('verbose') != None:
        if d['verbose'].lower() == 'true': verbose = True
        
    # determine if this is a request for 'hard' mode (narrower spikes)
    hardMode = False
    if d.get('setting') != None:
        if d['setting'] == 'hard': hardMode = True

    # check to see if the coordinates have at least been mentioned
    if d.get('x') == None: rs += 'your request is missing the x coordinate: for example x=4.\n'
    if d.get('y') == None: rs += 'your request is missing the y coordinate: for example y=3.\n'
    if d.get('z') == None: rs += 'your request is missing the z coordinate: for example z=1.\n'
    
    if len(rs) > 0: return { "statusCode": 200, "body": rs }

    if not d['x']: rs += 'request mentions x but please set it to something, for example x=4.\n'       
    if not d['y']: rs += 'request mentions y but please set it to something, for example y=3.\n'       
    if not d['z']: rs += 'request mentions z but please set it to something, for example z=1.\n'       
        
    if len(rs) > 0: return { "statusCode": 200, "body": rs }
        
    x = float(d['x'])
    y = float(d['y'])
    z = float(d['z'])
    
    s = sqrt(x*x + y*y + z*z)
    if s < 100.: pDroneLost = 0.0
    elif s < 1000.: pDroneLost = 0.05
    elif s < 2000.: pDroneLost = 0.12
    else: pDroneLost = 0.25
    
    bees = baseDensity + uniform(uniformLow, uniformHigh)
    
    for i in range(nHives):
        dx = x - c[i][0]
        dy = y - c[i][1]
        dz = z - c[i][2]
        gx = exp(-dx**2/(2.*sigma[0]**2))
        gy = exp(-dy**2/(2.*sigma[1]**2))
        gz = exp(-dz**2/(2.*sigma[2]**2))
        bees += 600.*(gx*gy*gz)
    
    if uniform(0., 1.) < pDroneLost: rs += 'drone lost'
    else: rs += str(int(floor(bees)))
    
    if verbose: 
        rs += ' ({}, {}, {})'.format(str(x), str(y), str(z))
        if hardMode: rs += ' (hard mode)'
    return { "statusCode": 200, "body": rs }
```

