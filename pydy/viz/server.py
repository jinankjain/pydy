#!/usr/bin/env python

import os
import sys
import signal
import socket
import webbrowser

# For python 2 and python 3 compatibility
if sys.version_info < (3, 0):
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from BaseHTTPServer import HTTPServer
else:
    from http.server import SimpleHTTPRequestHandler
    from http.server import HTTPServer
    raw_input = input

__all__ = ['Server']


class StoppableHTTPServer(HTTPServer):
    """
    Overrides BaseHTTPServer.HTTPServer to include a stop
    function.
    """

    def server_bind(self):
        HTTPServer.server_bind(self)
        self.socket.settimeout(1)
        self.run = True

    def get_request(self):
        while self.run:
            try:
                sock, addr = self.socket.accept()
                sock.settimeout(None)
                return (sock, addr)
            except socket.timeout:
                pass

    def stop(self):
        self.run = False

    def serve(self):
        while self.run:
            try:
                self.handle_request()
            except TypeError:
                # When server is being closed, while loop can run once
                # after setting self.run = False depending on how it
                # is scheduled.
                pass


class Server(object):
    """
    Parameters
    ----------
    port : integer
        Defines the port on which the server will run.
    scene_file : name of the scene_file generated for visualization
        Used here to display the url

    Example
    -------
    >>> server = Server(scene_file=_scene_json_file)
    >>> server.run_server()

    """
    def __init__(self, port=8000, scene_file="Null"):
        self.port = port
        self.scene_file = scene_file
        self.directory = "static/"

    def run_server(self):
        # Change dir to static first.
        os.chdir(self.directory)
        handler_class = SimpleHTTPRequestHandler
        server_class = StoppableHTTPServer
        protocol = "HTTP/1.0"
        server_address = ('127.0.0.1', self.port)
        handler_class.protocol_version = protocol
        self.httpd = server_class(server_address, handler_class)
        sa = self.httpd.socket.getsockname()
        print("Serving HTTP on", sa[0], "port", sa[1], "...")
        print("To view visualization, open:\n")
        url = "http://localhost:"+str(sa[1]) + "/index.html?load=" + \
              self.scene_file
        print(url)
        webbrowser.open(url)
        print("Hit Ctrl+C to stop the server...")
        signal.signal(signal.SIGINT, self._stop_server)
        self.httpd.serve()

    def _stop_server(self, signal, frame):
        """
        Confirms and stops the visulisation server
        signal:
            Required by signal.signal
        frame:
            Required by signal.signal

        """
        res = raw_input("Shutdown this visualization server ([y]/n)? ")
        res = res.lower()[0:1]
        if res == '' or res == 'y':
            print("Shutdown confirmed")
            print("Shutting down server...")
            self.httpd.stop()
        else:
            print("Resuming operations...")
