from datetime import datetime
import jwt
import time

import requests
import json

def encrypt_jwt(token, keyfile_path):
	keyfile = open(keyfile_path,'r') 
	private_key = keyfile.read()
	jwttoken = jwt.encode(token, private_key, algorithm='RS256')
	return jwttoken

def getToken(org_id, tech_account, client_id, expiration_days):
	return {
		"exp": int(round(time.time() * 1000)) + (expiration_days * 24 * 60 * 60 * 1000),
		"iss": org_id,
		"sub": tech_account,
		"https://ims-na1.adobelogin.com/s/ent_analytics_bulk_ingest_sdk": True,
		"aud": "https://ims-na1.adobelogin.com/c/{}".format(client_id)
	}

def authorize(client_id, client_secret, token):
	#orchastration_endpoint = request.args.get('orchastration_endpoint')

	# Adobe JWT authorization url
	authorization_url = 'https://ims-na1.adobelogin.com/ims/exchange/jwt'
	
	# Store required parameters in a dictionary
	params = {}
	params['jwt_token'] = token
	params['client_id'] = client_id
	params['client_secret'] = client_secret

	print(params)

	# This will prompt users with the approval page if consent has not been given
	# Once permission is provided, users will be redirected to the specified page
	result = requests.post(authorization_url, data = params)
	resultjson = json.loads(result.text)
	return resultjson