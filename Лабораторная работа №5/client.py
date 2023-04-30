import argparse
import os
import socket
from datetime import datetime

from http_utils import HTTPRequest, HTTPResponse
from logger_utils import Logger

logger = Logger("client.log")

parser = argparse.ArgumentParser()
parser.add_argument('address')
parser.add_argument('port')
parser.add_argument('file')
parser.add_argument('method')
parser.add_argument('-H', '--headers', nargs='*')
parser.add_argument('-d', '--data')
parser.add_argument('-t', '--template', nargs='*')

args = parser.parse_args()

# print(args)

address = args.address
port = int(args.port)
file = args.file
method = args.method

headers = args.headers

data = args.data
if data is None:
    data = ""

else:
    if not os.path.exists(data):
        print("Error: wrong path to file")
        exit(1)

    with open(data, "rb") as f:
        data = f.read()

template = ""
template_args = args.template
if template_args != []:
    path_to_file = template_args[0]
    template_args = template_args[1:]

    if not os.path.exists(path_to_file):
        print(f"Error: file {os.path.basename(path_to_file)} doesn't exist")
        exit(1)

    with open(path_to_file) as f:
        template = f.read()

    try:
        template = template.format(*template_args)

    except:
        print(f"Error: not enough arguments for template {os.path.basename(path_to_file)}")

if template != "" and data != "":
    print("Error: template and data command-line arguments are incompatible simultaneosly")
    exit(1)

logger.write("[INFO] Client arguments are ready")

request = HTTPRequest()
if method == "GET":
    request.set_start("GET", os.path.join('/', file))

    if data != "":
        request.set_body(data)

    if template != "":
        request.set_body(template)

elif method == "POST":
    request.set_start("POST", os.path.join('/', file))
    
    if data != "":
        request.set_body(data)

    if template != "":
        request.set_body(template)

elif method == "OPTIONS":
    request.set_start("OPTIONS", os.path.join('/', file))

else:
    print("Error: wrong method.")
    exit(1)

for header in headers:
    request.add_raw_header(header)

logger.write("[INFO] Request message is ready")
logger.write(f"[INFO] Trying to estabilish connection with {address}")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((address, port))

logger.write(f"[INFO] Connection with {address} is estabilished")
logger.write("[INFO] Message sending is started")
msg = request.encode()
to_send = len(msg)
while to_send > 0:
    to_send -= sock.send(msg)

logger.write("[INFO] Message is sucessfully sent")

msg = ""
end = False
is_decoded = False
byte_buffer = b""
while not end:
    data = sock.recv(1024)
    try:
        decoded = (byte_buffer + data).decode()
        is_decoded = True
        
    except:
        byte_buffer += data
        is_decoded = False

    if is_decoded:
        msg += decoded
        byte_buffer = b""
        end, request = HTTPResponse.parse(msg)


logger.write("[INFO] Message from server is sucessfully recieved")

print(msg)

sock.shutdown(socket.SHUT_RDWR)
sock.close()