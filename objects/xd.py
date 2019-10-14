import os

sitePath = "ficbook.net"
ficListByCategoryPath = "fanfiction"
ficListByTagPath = "tags"
ficPath = "readfic"

version = "0.1a"
port = int(os.getenv('VCAP_APP_PORT', 3001))
host = os.getenv('VCAP_APP_HOST', 'localhost')

threads = 16
requests = 0
debug = True

application = None
pool = None
busy = 0