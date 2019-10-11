import adobe-analytics-api as api
import authentication as auth

client_id = 'CLIENT_ID'
secret = 'CLIENT_SECRET'
org_id = 'ORG_ID'
tech_account = 'TECH_ACCOUNT'
keyfile_path = 'KEYFILE_PATH'
company_id = 'rcci1'

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
	"end_date":"2016-01-31T23:59:59.999".
    "segments": "" #""|["SEGMENT1","SEGMENT2",...]
}

token = auth.authorize(client_id, secret, org_id, tech_account, keyfile_path)

response = api.report(token['access_token'], client_id, company_id, definition.reportsuite, definition.dimensions, definition.metrics, definition.start_date, definition.end_date, segments = definition.segments)