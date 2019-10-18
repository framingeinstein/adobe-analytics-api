adobe-analytics-api - An Adobe Analytics API 2.0 library for python
====================
Installation
------------
You can install this through pip: pip install adobe-analytics-api_20

Usage
------------
```python
from  adobe_analytics import api
import authentication as auth

config = {
    'client_id' : 'CLIENT_ID',
    'client_secret' : 'CLIENT_SECRET',
    'org_id' : 'ORG_ID',
    'tech_account' : 'TECH_ACCOUNT',
    'keyfile_path' : 'KEYFILE_PATH',
    'company_id' : 'COMPANY_ID'
}

definition = {
    "reportsuite":"report-suite",
    "start_date": "2019-10-01",
    "end_date": "2019-10-01",
    "dimensions":["Day", "variables/evar50"],
    "metrics":[{"name":"metrics/orders"}, {"name": "metrics/revenue"}],
    "segments":["Name|id of a Segment"]
}

jwt_token = auth.getToken(config["org_id"], config["tech_account"], config["client_id"], 3)
print(jwt_token)
jwt = auth.encrypt_jwt(jwt_token, config["keyfile_path"])
print(jwt)
token = auth.authorize(config["client_id"], config["client_secret"], jwt)
print(token)
response = api.report(token['access_token'], config["client_id"], config["company_id"], definition["reportsuite"], definition["dimensions"], definition["metrics"], definition["start_date"], definition["end_date"], segments = definition["segments"])

print(response)
```