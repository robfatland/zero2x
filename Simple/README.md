# Simple example

Here is some Lambda code.

```
import json
import math
# from numpy import sqr

def lambda_handler(event, context):
    x = float(event["queryStringParameters"]['x'])
    xmo = x - 1.
    s = 1.
    s += xmo/2.
    s -= xmo*xmo/8.
    s += xmo*xmo*xmo/16.
    s -= (5./128.)*xmo*xmo*xmo*xmo
    # if x < 0.: sqrtx = 'something times i'
    # else: sqrtx = str(np.sqrt(x))
    # rtn_sqrtx = str(s)
    rtn_sqrtx = str(math.sqrt(x))
    return { "statusCode": 200, "body": rtn_sqrtx }
```

So this plus an API Gateway connected as input to the Lambda gets the job done.

