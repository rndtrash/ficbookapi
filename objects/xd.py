import os

sitePath = "ficbook.net"
ficFindPath = "find"
ficPath = "readfic"

version = "0.1a"
port = int(os.getenv('VCAP_APP_PORT', os.getenv('PORT', 8080)))
host = os.getenv('VCAP_APP_HOST', '0.0.0.0')

threads = 16
requests = 0
debug = True

application = None
pool = None
busy = 0