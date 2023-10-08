#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    # def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return data.split(" ")[1]

    def get_headers(self, data):
        return data.split("\r\n\r\n")[0]

    def get_body(self, data):
        return data.split("\r\n\r\n")[1]

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        print(f"getting {url}")
        port = 80
        p_url = urllib.parse.urlparse(url)
        host = p_url.netloc
        if p_url.path.endswith("/"):
            host += p_url.path[0:len(p_url.path) - 1]
        else:
            host += p_url.path
        if p_url.query != "":
            host += "?" + p_url.query
        if p_url.fragment != "":
            host += "#" + p_url.fragment
        if p_url.scheme == "https":
            port = 443

        payload = f'GET / HTTP/1.1\r\nHost: {host}\r\n\r\n'

        try:
            self.connect(host, port)
        except:

            print(f"Could not connect to host: {host}")
            self.connect(host, port)

            return HTTPResponse(404, '')
        self.sendall(payload)
        self.socket.shutdown(socket.SHUT_WR)
        content = self.recvall(self.socket)
        code = self.get_code(content)
        headers = self.get_headers(content)

        if (code.startswith("3")):
            # this is a redirect code
            for header in headers.split("\n"):
                if header.upper().startswith("LOCATION"):
                    location = header.split(" ")[1]
                    self.GET(location)

        code = int(code)
        body = self.get_body(content)
        self.close()
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        port = 80
        p_url = urllib.parse.urlparse(url)
        """
        host = p_url.netloc + p_url.path
        if p_url.query != "":
            host += "?" + p_url.query
        if p_url.fragment != "":
            host += "#" + p_url.fragment
            """
        if p_url.scheme == "https":
            port = 443

        payload = f'post {p_url.path} http/1.1\r\nHost: {p_url.netloc}\r\n\r\n' + p_url.query

        host = p_url.netloc
        print(f"Posting to host {host}")
        try:
            self.connect(host, port)
        except:
            print(f"Could not connect to host: {host}")
            return HTTPResponse(404, '')
        self.sendall(payload)
        self.socket.shutdown(socket.SHUT_WR)
        content = self.recvall(self.socket)
        print(content)
        code = 500
        body = ""
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
