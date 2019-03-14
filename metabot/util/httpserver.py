"""Complex-UI configuration interface."""

from __future__ import absolute_import, division, print_function, unicode_literals

try:
    import http.server as BaseHTTPServer
except ImportError:
    import BaseHTTPServer

import os
import json
import threading


class _RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):  # pylint: disable=invalid-name,missing-docstring
        if self.path == '/':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(
                open(os.path.join(os.path.dirname(__file__), 'httpserver.html'), 'rb').read())
        elif self.path == '/config':
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(self.server.multibot.conf).encode('ascii'))


class HTTPServer(BaseHTTPServer.HTTPServer):
    """Complex-UI configuration interface."""

    def __init__(self, multibot, port=0):
        self.multibot = multibot
        super(HTTPServer, self).__init__(('', port), _RequestHandler)

    def process_request(self, request, client_address):
        self.multibot.loop.queue.put(lambda: super(HTTPServer, self).process_request(
            request, client_address))

    def serve_forever_in_thread(self):
        """Run the server (self.serve_forever()) in a separate daemon thread."""

        thr = threading.Thread(target=self.serve_forever)
        thr.daemon = True
        thr.start()
