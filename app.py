# -*- coding: utf-8 -*-

from handlers import getFanficListHandler
from handlers import getFanficHandler

from objects import xd

from bottle import route, run

def main():

	print("> API listening on port {}".format(xd.port))

	run(host=xd.host, port=xd.port, debug=True)

@route("/")
def hello():
	return "get out of here, stalker"

if __name__ == "__main__":
	main()