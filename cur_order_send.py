import os
import time
import httplib2
import json
import sys
import base64
import hashlib
import hmac
from xml.dom import minidom

ACCESS_TOKEN = ''
SECRET_KEY = ''
CURRENCY = ''
ORDER = 'order'

# make payload
def get_encoded_payload(payload, qty, cur, kind):
	payload[u'nonce'] = int(time.time()*1000)
	if ORDER == kind:
		payload[u'qty'] = int(qty)
		payload[u'currency'] = cur

	dumped_json = json.dumps(payload)
	encoded_json = base64.b64encode(dumped_json)
	return encoded_json

# make signature
def get_signature(encoded_payload, secret_key):
	signature = hmac.new(str(secret_key).upper(), str(encoded_payload), hashlib.sha512);
	return signature.hexdigest()

# get api response
def get_api_response(url, payload, encoded_payload):
  headers = {
    'Content-type': 'application/json',
    'X-COINONE-PAYLOAD': encoded_payload,
    'X-COINONE-SIGNATURE': get_signature(encoded_payload, SECRET_KEY)
  }
  http = httplib2.Http()
  response, content = http.request(url, 'POST', headers=headers, body=encoded_payload)
  return content

# get URL address
def get_urlInfo(targetUrl):
	filePath = os.getcwd()
	filename = 'url_address.xml'
	url = ''

	fileInfo = '%s/%s' % (filePath, filename)

	urlDoc = minidom.parse(fileInfo)
	address = urlDoc.getElementsByTagName('urls')

	for info in address:
		if info.attributes['name'].value == targetUrl:
			url = info.firstChild.data

	return url

# get balance Information
def get_balance():
	url = get_urlInfo('balance'):
	payload = {
		'access_token': ACCESS_TOKEN,
	}

	encoded_payload = get_encoded_payload(payload, '', '', '')

	response = get_api_response(url, payload, encoded_payload)
	content = json.loads(response.content)

	return content


# make sell order
def send_message_order(cur):
	# get balance
	balance = get_balance()
	qty = balance[cur]['avail']

	url = get_urlInfo('sellOrder'):
	payload = {
		'access_token': ACCESS_TOKEN,
	}
	
	encoded_payload = get_encoded_payload(payload, qty, cur, ORDER)
	response = get_api_response(url, payload, encoded_payload)
	content = json.loads(response.content)
	
	return response

if __name__ == "__main__":
	CURRENCY = 'btc'
	print send_message_order(CURRENCY)