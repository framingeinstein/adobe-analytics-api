import os
import requests
from six.moves import urllib
import json
import uuid
import pandas as pd
from datetime import datetime
import time
import curlify


class APIException(Exception):
	

	def __init__(self, message, status_code=None, payload=None):
		Exception.__init__(self)
		self.message = message
		self.status_code = 500
		if status_code is not None:
			self.status_code = status_code
		self.payload = payload

	def to_dict(self):
		print(self.message)
		rv = {}
		try:
			rv = dict(self.payload or ())
		except:
			rv = {}

		rv['message'] = self.message
		rv['status_code'] = self.status_code
		rv['payload'] = self.payload
		return rv	


def error_check(data):
	if 'error_code' in data:
		message = data['message'] if 'message' in data else data['error_code']
		print(data)
		raise APIException(message, payload={'error_code': data['error_code']})
	return data

def request_metrics(access_token, client_id, company_id, rsid):
	params = {
		'rsid': rsid
	}
	
	response = requests.get('https://analytics.adobe.io/api/{}/metrics'.format(company_id),
		params = params,
		headers = {'Authorization': 'Bearer {}'.format(access_token), 'x-api-key': client_id, 'x-proxy-global-company-id': company_id, 'Content-Type': "application/json"}
		#data = json.dumps(req))
	)
	
	return error_check(response.json())

def request_dimensions(access_token, client_id, company_id, rsid):
	params = {
		'rsid': rsid
	}
	
	response = requests.get('https://analytics.adobe.io/api/{}/dimensions'.format(company_id),
		params = params,
		headers = {'Authorization': 'Bearer {}'.format(access_token), 'x-api-key':client_id, 'x-proxy-global-company-id': company_id, 'Content-Type': "application/json"}
		#data = json.dumps(req))
	)

	return error_check(response.json())

def request_segments(access_token, client_id, company_id, rsid=None, limit=1000):
	
	params = {
		'limit': limit,
		'includeType': 'all'
	}

	if rsid is not None:
		params['rsids'] = rsid

	response = requests.get('https://analytics.adobe.io/api/{}/segments'.format(company_id),
		params = params,
		headers = {'Authorization': 'Bearer {}'.format(access_token), 'x-api-key': client_id, 'x-proxy-global-company-id': company_id, 'Content-Type':"application/json", "Accept":"application/json"}
		#data = json.dumps(req))
	)
	#print(curlify.to_curl(response.request))
	return error_check(response.json())['content']

def request_calculatedmetrics(access_token, client_id, company_id, rsid=None, limit=300):
	
	params = {
		'limit': limit,
		'includeType': 'all'
	}
	if rsid is not None:
		params['rsids'] = rsid
	
	response = requests.get('https://analytics.adobe.io/api/{}/calculatedmetrics'.format(company_id),
		params = params,
		headers = {'Authorization': 'Bearer {}'.format(access_token), 'x-api-key': client_id, 'x-proxy-global-company-id': company_id, 'Content-Type': "application/json"}
		#data = json.dumps(req))
	)
	#print(curlify.to_curl(response.request))
	return error_check(response.json())['content']


def request_suites(access_token, client_id, company_id, rsid):
	params = {
		'rsid': rsid
	}
	
	response = requests.get('https://analytics.adobe.io/api/{}/collections/suites'.format(company_id),
		params = params,
		headers = {'Authorization': 'Bearer {}'.format(access_token), 'x-api-key': client_id, 'x-proxy-global-company-id': company_id, 'Content-Type': "application/json"}
		#data = json.dumps(req))
	)

	return response.json()

def request_builder(rsid, date_start, date_end, dimension, metrics, breakdown=None, id=None, segments=None, limit=10000, page=0, countRepeatInstances=True):
	m = []
	b = []
	for i, metric in metrics.iterrows():
		
		t = {'columnId':str(i), 'id':metric['id']}
		t['filters'] = []
		if breakdown:
			t['filters'].append(str(i))
			l = {
				"id" : str(i),
				"type": "breakdown",
				"dimension": breakdown,
				"itemId": str(id)
			}
			b.append(l)
		if 'filter' in metric and not pd.isna(metric['filter']):
			seg = {
				"type":"segment",
				"segmentId": metric['filter']
			}
			seg['id'] = str(len(b))
			b.append(seg)
			
			t['filters'].append(seg['id'])
		m.append(t)

	filters = []
	
	#Handle dates without timestamps, asumming date range is meant to be inclusive
	if len(date_start) == 10:
		date_start = "{}T{}".format(date_start, "00:00:00")
	if len(date_end) == 10:
		date_end = "{}T{}".format(date_end, "23:59:59")
	filters.append({
		"type": "dateRange",
		"dateRange": "{}/{}".format(date_start, date_end)
	})
	
	if segments is not None  and segments != '':
		for segment in segments:
			filters.append({
				"type": "segment",
				"segmentId":segment
			})

	return {
		"rsid": rsid,
		"globalFilters": filters,
		"metricContainer": {
			"metrics": m,
			"metricFilters": b
		},
		"dimension":dimension,
		"settings": {
			"countRepeatInstances": countRepeatInstances,
			"limit": limit,
			"page": page
		}
	}

def request_report(access_token, client_id, company_id, definition, fetchall=True):
	if 'page' not in definition['settings']:
		 definition['settings']['page'] = 0

	params = {
		'client_id' : client_id
	}

	response = requests.post('https://analytics.adobe.io/api/{}/reports'.format(company_id),
		#params = params,
		headers = {'Authorization': 'Bearer {}'.format(access_token), 'x-api-key': client_id, 'x-proxy-global-company-id': company_id, 'Content-Type': "application/json"},
		data = json.dumps(definition))

	data = error_check(response.json())
	if 'errorCode' in data:
		print(data)
		raise APIException(data['errorCode'], payload=data)

	if 'rows' not in data:
		raise APIException('EmptyReport', payload={'definition': definition, 'result': data})

	if fetchall:
		rows = data['rows']
		while not data['lastPage'] and data['totalPages'] != 0:
			definition['settings']['page'] = definition['settings']['page'] + 1
			data = request_report(access_token, client_id, company_id, definition, False)
			rows = rows + data['rows']
		data['rows'] = rows
		return data
	return data

def normalize_data(definition, data):
	columns = definition['metricContainer']['metrics']
	dimension = data['columns']['dimension']
	
	rows = data['rows']
	da = []
	for row in rows:
		d = {}
		d[dimension['id']] = row['value']
		d[dimension['id']+'_itemId'] = row['itemId']
		for i, column in enumerate(columns):
			d[column['id']] = row['data'][i]
		da.append(d)
	df = pd.DataFrame(da)
	return df

#datarange, elements, metrics, segments

def map_dimensions(dimensions, access_token, client_id, company_id, rsid):

	element_lookup = request_dimensions(access_token, client_id, company_id, rsid)

	dims = pd.DataFrame(element_lookup)
	dims = dims[(dims.id.isin(dimensions)) | (dims.name.isin(dimensions))]
	if len(dims) > len(dimensions):
		raise APIException("Multiple dimensions found with for supplied dimentsions", payload=dims[['id','name']].to_json(orient='records'))
	if len(dims) < len(dimensions):
		raise APIException("Invalid dimensions supplied", payload=dims[['id','name']].to_json(orient='records'))
	return dims[['id','name', 'type']]

def map_metrics(metrics, access_token, client_id, company_id, rsid):


	metric_lookup = request_metrics(access_token, client_id, company_id, rsid)
	#print(metric_lookup)
	print("=====================================")
	mets = pd.DataFrame(metric_lookup)

	cmetric_lookup = request_calculatedmetrics(access_token, client_id, company_id, rsid)
	#print(cmetric_lookup)
	cmets = pd.DataFrame(cmetric_lookup)

	#print(cmets)
	if len(cmets) > 0:
		print("Merging Calculated Metrics With Standard Metrics")
		mets = pd.concat([mets[['id','name', 'type']], cmets[['id','name', 'type']]])
	
	metrics = pd.DataFrame(metrics)

	mets1 = pd.merge(mets, metrics, on='name')

	mets2 = pd.merge(mets, metrics, left_on='id', right_on='name')
	mets2.drop(["name_y"], axis=1, inplace=True)
	mets2.rename(columns={'name_x':'name'}, inplace=True)

	mets = pd.concat([mets1, mets2]).reset_index(drop=False)
	#Handle not rename_to columns
	if 'rename_to' not in mets:
		mets['rename_to'] = mets['name']
	if 'filter' not in mets:
		mets['filter'] = None
	mets['rename_to'] = mets['rename_to'].fillna(mets['name'])
	mets.drop_duplicates(subset ="name", keep = False, inplace = True)
	print(mets)
	print(metrics)
	if len(mets) > len(metrics):
		raise APIException("Multiple metrics Found with for supplied metrics", payload=mets[['id','name']].to_json(orient='records'))
	if len(mets) < len(metrics):
		notfound = [x for x in metrics if x not in mets['id'].tolist() and x not in mets['name'].tolist()]
		raise APIException("Invalid metrics supplied: {}".format(notfound))
	return mets[['id','name', 'type', 'filter', 'rename_to']]

def map_segments(segments, access_token, client_id, company_id, rsid=None):

	segment_lookup = request_segments(access_token, client_id, company_id, rsid=rsid)
	if len(segment_lookup) == 0:
		segment_lookup = [
			{"id":"NA", "name":"NA"}
		]
	mets = pd.DataFrame(segment_lookup)

	mets = mets[(mets.id.isin(segments)) | (mets.name.isin(segments))]
	if len(mets) > len(segments):
		raise APIException("Multiple segments Found with for supplied segments", payload=mets[['id','name']].to_json(orient='records'))
	if len(mets) < len(segments):
		raise APIException("Invalid segments supplied", payload=mets[['id','name']].to_json(orient='records'))
	return mets[['id','name']]


def report(access_token, client_id, company_id, rsid, dimensions, metrics, date_start, date_end, segments=None, parent=None, row=None):
	
	# only do this  the first time this is called... this can be cached more agressively later
	md = map_dimensions(dimensions, access_token, client_id, company_id, rsid)
	mm = map_metrics(metrics, access_token, client_id, company_id, rsid)
	ms = None
	if segments == '':
		segments = None
	if segments is not None:
		ms = map_segments(segments, access_token, client_id, company_id, rsid)

	#ensure ids
	dimensions = md['id'].tolist()
	data_type = md['type'].tolist().pop(0)
	dimension = dimensions.pop(0)

	kargs = {}
	if parent and row:
		kargs['breakdown'] = parent['columns']['dimension']['id']
		kargs['id'] = row['itemId']

	if ms is not None:
		kargs['segments'] = ms['id'].tolist()

	req =  request_builder(rsid, date_start, date_end, dimension, mm, **kargs)
	print(req)
	data = request_report(access_token, client_id, company_id, req)
	data = error_check(data)
	df = normalize_data(req, data)
	
	if len(dimensions) > 0:
		#Remove metrics columns as these are only needed for then last element
		print("+++++================++++++++++")
		print(df.columns)
		print("+++++================++++++++++")
		for i, column in enumerate(req['metricContainer']['metrics']):
			if(column['id'] in df.columns):
				df.drop(column['id'], 1, inplace=True)

		dfa = []
		for row in data['rows']:
			# @TODO: This will need to be dialed in as well as the number of workers in the worker app
			# We need to throttle this so we do not hit api errors and have to start over.  
			time.sleep(1) # 1 second
			result = report(access_token, client_id, company_id, rsid, dimensions[:], metrics, date_start, date_end, segments, parent=data, row=row)
			#row['children'] = result
			result['parent_itemId'] = row['itemId']
			dfa.append(result)
		m = pd.concat(dfa, sort=True)

		df = pd.merge(m, df, right_on=data['columns']['dimension']['id'] + '_itemId' ,left_on='parent_itemId')

		# drop join fields
		df.drop(['parent_itemId', '{}_itemId'.format(data['columns']['dimension']['id'])], axis=1, inplace=True)
		# Lets change to friendly names
	
	if data_type == 'time':
		df[dimension] = pd.to_datetime(df[dimension])
	
	
	if parent is None:
		cols = []
		#I am the root node in the recursion tree so let's order the data according to the way the definition specified
		# dimensions then metrics

		dimensions.insert(0, dimension)
		for d in dimensions:
			dims = md[(md.id.isin([d])) | (md.name.isin([d]))]
			dim_id = dims.iloc[0]['id']
			cols.append(dim_id)
		for d in metrics:
			mets = mm[(mm.id.isin([d['name']])) | (mm.name.isin([d['name']]))]
			met_id = mets.iloc[0]['id']
			cols.append(met_id)

			data_type = mets.iloc[0]['type']
			#take care of typing
			print("Data Type for column {} is {}".format(mets.iloc[0]['name'], data_type))
			if(data_type == 'int'):
				print("casting")
				df = df.astype({met_id: 'int'})
				df = df.round({met_id: 0})
			if(data_type == 'decimal'):
				print("casting")
				df = df.astype({met_id: 'int'}) #We are going to round to whole dollars..  I want this to be more flexible though.
				df = df.round({met_id: 0})
			if(data_type == 'currency'):
				print("casting")
				df = df.astype({met_id: 'float'})
				df = df.round({met_id: 2})
				
		df = df[cols]

		df.rename(columns={d['id']: d['name'] for d in md.to_dict(orient='records')}, inplace=True)
		df.rename(columns={d['id']: d['rename_to'] for d in mm.to_dict(orient='records')}, inplace=True)
		
	return df

#{"metrics": ["metrics/event38", "metrics/event29"], "reportsuite": "royalcaribbeanprod", "elements": ["variables/daterangeday"], "start_date": "2018-11-01T00:00:00.000", "end_date": "2018-11-30T23:59:59.999"}
#access_token = "eyJ4NXUiOiJpbXNfbmExLWtleS0xLmNlciIsImFsZyI6IlJTMjU2In0.eyJpZCI6IjE1NDUwOTkyMzgzNzhfZmUyNzQ4MTEtOTFjYS00MWYwLWIxYzctZGQxN2MzODBjNzc0X3VlMSIsImNsaWVudF9pZCI6IjkxYzAzNzgxMDJmMjQ2ZmI5ZjA5NjYxMThmZmRlMmMzIiwidXNlcl9pZCI6IjczNDk0RUJBNUIyODAzMEUwQTQ5NUNFQUBBZG9iZUlEIiwic3RhdGUiOiIiLCJ0eXBlIjoiYWNjZXNzX3Rva2VuIiwiYXMiOiJpbXMtbmExIiwiZmciOiJUQVhVSzdLWlhMUDM3SEdXMjROUUFBQUFIUT09PT09PSIsInNpZCI6IjE1NDUwOTkyMzgwMzdfOGE3NTU5NzgtMmRkNS00YTQwLThiMDctMTFmOGRhZjA4ODAyX3VlMSIsInJ0aWQiOiIxNTQ1MDk5MjM4Mzc5X2ZhMDRkODI4LWVmNzgtNDAwZS1hNDQzLTUzYTJjYWUzY2U5MV91ZTEiLCJvYyI6InJlbmdhKm5hMXIqMTY3YmYxNzU5ZjQqREpaWlE0MDhFWDNTNTk0SkRFOFc3UjNQVEMiLCJydGVhIjoiMTU0NjMwODgzODM3OSIsIm1vaSI6IjI2NTY4OWIxIiwiYyI6IkJwaXlsQ2tEcmZ3aWVtMy9ZZms3d2c9PSIsImV4cGlyZXNfaW4iOiI4NjQwMDAwMCIsInNjb3BlIjoib3BlbmlkLEFkb2JlSUQscmVhZF9vcmdhbml6YXRpb25zLGFkZGl0aW9uYWxfaW5mby5qb2JfZnVuY3Rpb24sYWRkaXRpb25hbF9pbmZvLnByb2plY3RlZFByb2R1Y3RDb250ZXh0IiwiY3JlYXRlZF9hdCI6IjE1NDUwOTkyMzgzNzgifQ.kEJh6ucvmSXt8RQjOQgBbgGzqJWKSqF9PDUm2sWjQiWkvm9ge_hkeYUo4JsHkHRrlMcbp568JzT77xfPPGLYTYXyOFhecy00A_ioNIQRXNtep1pzoaDWSGtYv5E4qnpxp6htiRZMGllFW6i1LslBaokUrb4ACHdnRn1beBIu8vQLNpCMoOkO7Io2O7VikrU6kshWw9btjKk-zzcQUKIv5SKKlDqSZ0KJdkvMByX8y0NULP427pNoCTCk1IrXgkJoYTfQEVcHOMIkqJKF1TQ-hP-PczKr83tny3C1ayvz-SNx5cxFP9kHEt7sk1byRXh1qdkt15xOLFHrV67VQwtf4w"
#req  = {"metrics": ["metrics/event38", "Emails Delivered (ET Total)"], "reportsuite": "royalcaribbeanprod", "elements": ["Day","variables/campaign"], "start_date": "2018-11-01T00:00:00.000", "end_date": "2018-11-30T23:59:59.999", "segments": ["AeM: EMAIL MARKETING CHANNEL (new) - 06082015 - visit"]}
"""
d = map_dimensions(req['elements'], access_token, "91c0378102f246fb9f0966118ffde2c3", "rcci1", "royalcaribbeanprod")
print(d[['id','name']])

d = map_metrics(req['metrics'], access_token, "91c0378102f246fb9f0966118ffde2c3", "rcci1", "royalcaribbeanprod")
print(d[['id','name']], len(d), d[['id','name']].to_json(orient='records'))



d = map_segments(req['segments'], access_token, "91c0378102f246fb9f0966118ffde2c3", "rcci1")
print(d[['id','name']], len(d), d[['id','name']].to_json(orient='records'))
"""

#Email stats - Sent|TotalOpens|UniqueOpens|TotalClicks|UniqueClicks|Unsubs|Bounces

#Web stats - Total + Only from Email
#Page Views, Visits, Campaign Clickthroughs (email only), Cruise Purchases, Cruise Revenue, PCP Purchases, PCP Revenue
"""
data = request_calculatedmetrics(access_token, "91c0378102f246fb9f0966118ffde2c3", "rcci1")

with open('rcci_calculatedmetrics.json', 'w') as outfile:
    json.dump(data, outfile, indent=4, sort_keys=True)

segs = request_segments(access_token, "91c0378102f246fb9f0966118ffde2c3", "rcci1")

data = request_metrics(access_token, "91c0378102f246fb9f0966118ffde2c3", "rcci1", "royalcaribbeanprod")

with open('rcci_metrics.json', 'w') as outfile:
    json.dump(data, outfile, indent=4, sort_keys=True)
"""

"""
definition = {  
    "metrics":[  
        {"name": "metrics/event38"},
		{"name": "metrics/event29"}, 
		{"name": "metrics/event30"}, 
		{"name": "metrics/event31"}, 
		{"name": "metrics/event32"},
		{"name": "metrics/event33"}, 
		{"name": "metrics/event94"}, 
		{"name": "metrics/event95"},
		{"name": "Page Views"},
		{"name": "Visits"}, 
		{"name": "metrics/campaigninstances", "filter":"s300006910_5a99c3be8b49b77306aefc87", "rename_to": "Campaign Clickthroughs (email only)"}, 
		{"name": "Orders (Incl. Bookings)", "rename_to": "Cruise Purchases"}, 
		{"name": "Revenue", "rename_to": "Cruise Revenue"}, 
		{"name": "PCP purchase (Counter)", "rename_to": "PCP Purchases"}, 
		{"name": "PCP purchase (Invoiced)", "rename_to": "PCP Revenue"}
    ],
    "reportsuite":"royalcaribbeanprod",
    "elements":[  
        "Day" #Day|Week|Year|Quarter
    ],
    "start_date":"2016-01-01T00:00:00.000",
    "end_date":"2016-01-31T23:59:59.999"
}
try:
	#d = map_metrics(definition['metrics'], access_token, "91c0378102f246fb9f0966118ffde2c3", "rcci1", definition['reportsuite'])
	#print(d)
	r = report(access_token, "91c0378102f246fb9f0966118ffde2c3", "rcci1", definition['reportsuite'], definition['elements'], definition['metrics'], definition['start_date'], definition['end_date'])
	r = r[r.columns.drop(list(r.filter(regex='.*_itemId$')))]
	
	print(r)
except APIException as ex:
	print(ex.message)
"""
"""
# Request 1
req = {  
    "metrics":[  
        {"name": "metrics/event38"},
		{"name": "metrics/event29"}, 
		{"name": "metrics/event30"}, 
		{"name": "metrics/event31"}, 
		{"name": "metrics/event32"},
		{"name": "metrics/event33"}, 
		{"name": "metrics/event94"}, 
		{"name": "metrics/event95"},
		{"name": "Page Views"},
		{"name": "Visits"}, 
		{"name": "metrics/campaigninstances", "filter":"s300006910_5a99c3be8b49b77306aefc87", "rename_to": "Campaign Clickthroughs (email only)"}, 
		{"name": "Orders (Incl. Bookings)", "rename_to": "Cruise Purchases"}, 
		{"name": "Revenue", "rename_to": "Cruise Revenue"}, 
		{"name": "PCP purchase (Counter)", "rename_to": "PCP Purchases"}, 
		{"name": "PCP purchase (Invoiced)", "rename_to": "PCP Revenue"}
    ],
    "reportsuite":"royalcaribbeanprod",
    "elements":[  
        "Day"
    ],
    "start_date":"2016-01-01T00:00:00.000",
    "end_date":"2016-01-31T23:59:59.999"
}


#REQUEST 2
{  
    "metrics":[  
        "Page Views," 
		"Visits", 
		"Campaign Clickthroughs (email only)", 
		Cruise Purchases, 
		Cruise Revenue, 
		PCP Purchases, 
		PCP Revenue
    ],
    "reportsuite":"royalcaribbeanprod",
    "elements":[  
        "Day"
    ],
    "start_date":"2018-11-01T00:00:00.000",
    "end_date":"2018-11-30T23:59:59.999"
}

# Request 3
{  
    "metrics":[  
        "metrics/event38",
        "Emails Delivered (ET Total)"
    ],
    "reportsuite":"royalcaribbeanprod",
    "elements":[  
        "Day",
        "variables/campaign"
    ],
    "start_date":"2018-11-01T00:00:00.000",
    "end_date":"2018-11-30T23:59:59.999"
}

"""