#  coding: utf-8 
import socketserver
import pathlib


# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

def generate_response(res_code, msg, headers='', content=''):
    return f'HTTP/1.1 {res_code} {msg}\n{headers}\n\n{content}'


class MyWebServer(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        method = self.data.decode('ascii').split(" ")[0]
        requested_path = self.data.decode('ascii').split(" ")[1]

        print(method, requested_path)
        # 405 for non supported methods
        if method != 'GET':
            res = generate_response(405, "Method Not Allowed")
            self.request.sendall(res.encode())
            return

        # prevent access to files outside www and invalid files
        resolved_path = pathlib.Path(f'./www{requested_path}')
        if not resolved_path.resolve().as_posix().startswith(pathlib.Path('./www/').resolve().as_posix())\
                or not (resolved_path.is_file() or resolved_path.is_dir()):
            res = generate_response(404, "Not Found")
            self.request.sendall(res.encode())
            return

        if resolved_path.is_dir() and requested_path[-1] != '/':
            res = generate_response(301, "Moved Permanently", f"Location: http://127.0.0.1:8080{requested_path}/")
            self.request.sendall(res.encode());
            return

        if resolved_path.is_dir():
            file_path = pathlib.Path(resolved_path.as_posix() + '/index.html')
            if not file_path.is_file():
                res = generate_response(404, "Not Found")
                self.request.sendall(res.encode())
                return

            res = generate_response(200, "OK", f'Content-Type: text/{file_path.suffix.split(".")[1]}',file_path.read_text())
            self.request.sendall(res.encode())
            return

        content = resolved_path.read_text()
        res = generate_response(200, "OK", f'Content-Type: text/{resolved_path.suffix.split(".")[1]}', content)
        self.request.sendall(res.encode())
        return




if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
