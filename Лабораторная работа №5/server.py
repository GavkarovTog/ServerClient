import socket
import urllib.parse
import os
import argparse

from http_utils import HTTPResponse, HTTPRequest
from logger_utils import Logger

logger = Logger("server.log") # Set log file and create it if one doesn't exist

parser = argparse.ArgumentParser(prog="python server.py", 
                                 description="This program acts as a http server. It can handle GET, POST and OPTIONS methods")
parser.add_argument('-d', '--directory', help="Path to directory to share file from")
parser.add_argument('-p', '--port', help="Port on which server will expect for requests")

args = parser.parse_args()

dir_path = args.directory
if dir_path is None:
    dir_path = "./"

port = args.port
port = int(port) if port is not None else 8080

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', port))
sock.listen(1)

time_to_wait = 70
sock.settimeout(time_to_wait)

logger.write(f"[INFO] Server is started. Listening on {port}. Timeout on {time_to_wait} seconds.")

while True:
    conn, address = sock.accept() # Wait for connection
    logger.write(f"[INFO] {address[0]} connected to server")

    logger.write(f"[INFO] Server is waiting for request from {address[0]}")
    msg = ""
    request = None
    end = False
    while not end: # Read data from client 
        data = conn.recv(1024) # by 1024 bytes
        msg += data.decode("utf-8") # in buffer 'msg'

        try:
            end, request = HTTPRequest.parse(msg) # while it's not ended

        except HTTPIncompatibleVersionException:
            logger.write(f"[INFO] {address[0]} tried to use incompatible version of http in request")
            conn.shutdown(socket.SHUT_RDWR) # Tell client that work is end
            conn.close()
            continue

    logger.write(f"[INFO] {address[0]} has just sent request to server")

    print("Headers:")
    for key, value in request.headers.items():
        print(f"{key}: {value}")

    print("Body:")
    print(request.body.decode())

    method = request.method
    uri = request.uri

    response = HTTPResponse()
    additional_info = ""
    if method == "GET":
        parsed_url = urllib.parse.urlparse(uri)
        path_to_file = os.path.join(dir_path, urllib.parse.unquote_plus(parsed_url.path)[1:])
        additional_info = path_to_file
        
        if os.path.exists(path_to_file):
            file_content = ""

            with open(path_to_file, "rb") as f:
                file_content = f.read()
            
            response.set_start(200, "OK")
            response.set_body(file_content)
            if os.path.splitext(os.path.basename(path_to_file))[-1] == ".svg":
                response["Content-Type"] = "image/svg+xml"

        else:
            response.set_start(404, "Not Found")

        if request["Content-Length"] != 0:
            response["Received-Message"] = "We got your message"

    elif method == "POST":
        parsed_url = urllib.parse.urlparse(uri)
        path_to_file = os.path.join(dir_path, urllib.parse.unquote_plus(parsed_url.path)[1:])
        additional_info = path_to_file
        
        if os.path.exists(path_to_file):
            file_content = ""

            with open(path_to_file, "rb") as f:
                file_content = f.read()
            
            response.set_start(200, "OK")
            response.set_body(file_content)
            if os.path.splitext(os.path.basename(path_to_file))[-1] == ".svg":
                response["Content-Type"] = "image/svg+xml"

        else:
            response.set_start(404, "Not Found")

        if request["Content-Length"] != 0:
            response["Received-Message"] = request.body.decode()

    elif method == "OPTIONS":
        response.set_start(200, "OK")

    else:
        response.set_start(501, "Not Implemented")

    response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'

    logger.write(f"[{address[0]}]: {response.code} {response.reason} <- {additional_info}")

    # Send reply back to the 
    msg = response.encode() # client
    to_send = len(msg)
    while to_send != 0: # Send reply
        to_send -= conn.send(msg) # until all data is sent

    conn.shutdown(socket.SHUT_RDWR) # Tell client that work is end
    conn.close()    # Close socket object to become free and wait for new request