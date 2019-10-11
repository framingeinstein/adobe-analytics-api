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

	def authorize(client_id, client_secret, org_id, tech_account, keyfile_path):
		#orchastration_endpoint = request.args.get('orchastration_endpoint')
		params = request.get_json(force = True)

		#flask.session['orchastration_endpoint'] = orchastration_endpoint
		flask.session['client_id'] = client_id
		flask.session['client_secret'] = client_secret
		# Adobe JWT authorization url
		authorization_url = 'https://ims-na1.adobelogin.com/ims/exchange/jwt'
		
		# Store required parameters in a dictionary
		params = {}
		token = getToken(org_id, tech_account, client_id, 3)
		params['jwt_token'] = encrypt_jwt(token, keyfile_path)
		params['client_id'] = client_id
		params['client_secret'] = client_secret

		#print(params)

		# This will prompt users with the approval page if consent has not been given
		# Once permission is provided, users will be redirected to the specified page
		result = requests.post(authorization_url, data = params)
		resultjson = json.loads(result.text)
		return resultjson