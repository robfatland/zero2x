## Usage
Before executing the dynmo_upload.py initial setup requires setting up requisite credential file for AWS S3.

Provide one time key_id and key_access to be stored in the home folder as creds.json which will be used by dynmo_upload.py.

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
