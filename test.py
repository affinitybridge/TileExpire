from sys import stderr
from httplib import HTTPConnection
import json

conn = HTTPConnection('localhost', 8080)
conn.connect()

payload = {
    'zooms': [3],
    'bbox': [85, -180, -85, 180],
    'extension': 'png',
    'padding': 0
}
conn.request('POST', '/clean/wbc--resource-roads', json.dumps(payload))

response = conn.getresponse()
print >> stderr, 'Status: %(status)d - %(reason)s' % \
        {'status': response.status, 'reason': response.reason}

data = response.read()
print >> stderr, data

conn.close()
