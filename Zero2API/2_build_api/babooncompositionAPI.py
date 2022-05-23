import urllib.request, json, math
from json2html import *

def GetCoordList(indiv, t0, t1):
    print(indiv)
    baseURL = 'https://rlu4ch9a57.execute-api.us-west-2.amazonaws.com/default/baboon1'
    url     = baseURL + '?indiv={}&table=false&t0={}&t1={}'.format(indiv,t0,t1)
    with urllib.request.urlopen(url) as myurl: a = json.loads(myurl.read().decode())
    c = []
    if len(a) > 0:     # a being a list of dictionaries with keys 'x' and 'y'
    for b in a: c.append((b['x'], b['y']))
    return c


# Variant on the original moment of inertia using four time limits t0 t1 t2 t3
#   Return values are comma-separated text: moi1, moi2, n1, n2, s
#   Where: 
#     moi1 is for time interval t0-t1
#     moi2 is for time interval t2-t3
#     n1 is how many values were pulled for the t0-t1 interval
#     n2                                        t2-t3
#     s is the distance between center of mass (t0-t1) and center of mass (t2-t3)
                                            
    
def lambda_handler(event, context):
    # print(event)
    indivlist = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,18,20,21,23,24,25,31,33,35,38]
    params=event['queryStringParameters']
    if 't0' in params and 't1' in params and 't2' in params and 't3' in params:

        # print('calculating time-window moment of inertia')
        t0 = str(params['t0'])
        t1 = str(params['t1'])
        t2 = str(params['t2'])
        t3 = str(params['t3'])
        q = []
        r = []
        for i in indivlist: q.append(GetCoordList(i, t0, t1))     # a list of lists of tuples
        for i in indivlist: r.append(GetCoordList(i, t2, t3))     # a list of lists of tuples
        coords1 = []
        for qq in q:                                              # each qq is a list of tuples
            for qqq in qq:                                        # each qqq is a tuple (x, y)
                coords1.append(qqq)
        coords2 = []
        for rr in r:                                              # each qq is a list of tuples
            for rrr in rr:                                        # each qqq is a tuple (x, y)
                coords2.append(rrr)

        lencoords1 = float(len(coords1))
        lencoords2 = float(len(coords2))

        # first time interval: calculate moi1 and com (xbar1, ybar1)
        if lencoords1 > 0.:
            xsum, ysum, rsum = 0., 0., 0.
            for c in coords1:
                xsum += float(c[0])
                ysum += float(c[1])
            xbar1, ybar1 = xsum / lencoords1, ysum / lencoords1
            for c in coords1:
                dx, dy = float(c[0]) - xbar1, float(c[1]) - ybar1
                rsum += math.sqrt(dx*dx + dy*dy)
            moi1 = rsum/lencoords1
        else: moi1 = 0.

        # same with second time interval
        if lencoords2 > 0.:
            xsum, ysum, rsum = 0., 0., 0.
            for c in coords2:
                xsum += float(c[0])
                ysum += float(c[1])
            xbar2, ybar2 = xsum / lencoords2, ysum / lencoords2
            for c in coords2:
                dx, dy = float(c[0]) - xbar2, float(c[1]) - ybar2
                rsum += math.sqrt(dx*dx + dy*dy)
            moi2 = rsum/lencoords2
        else: moi2 = 0.

        if moi1 > 0. and moi2 > 0.: 
            dx = xbar1 - xbar2
            dy = ybar1 - ybar2
            s = math.sqrt(dx*dx + dy*dy)
        else: s = 0.

        response = '{},{},{},{},{}'.format(moi1, moi2, len(coords1), len(coords2), s)
    else:
        response = 'composition api: specify ?t0=hh:mm:ss&t1=hh:mm:ss&t2&t3 (likewise) > moi01, moi23, npts01, npts23, distance'
    return { "statusCode": 200, "body": response }
