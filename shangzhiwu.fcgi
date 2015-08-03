#!/usr/bin/python
from flup.server.fcgi import WSGIServer
from app import app

if __name__ == '__main__':
	WSGIServer(app, bindAddress='/var/tmp/shangzhiwu-fcgi.sock').run()
