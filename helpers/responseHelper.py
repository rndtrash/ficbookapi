import json

def pretty(object):
	return json.dumps(object, sort_keys=True,indent=4, ensure_ascii=False, separators=(',', ': ')).encode('utf-8')