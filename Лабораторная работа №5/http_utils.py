class HTTPMessage:
    def __init__(self):
        self.headers = {}
        self.body = b""

    def add_header(self, key, value):
        self.headers[key] = str(value)

    def add_raw_header(self, header):
        key, value, *other = header.split(":")
        self.headers[key] = (value + ":".join(other)).strip()

    def set_body(self, body):
        assert type(body) == str or type(body) == bytes, "Body must be either string type or bytes"

        if type(body) == str:
            self.body = body.encode("utf-8")

        else:
            self.body = body

        content_length = len(self.body)
        if content_length != 0:
            self["Content-Length"] = content_length

    def __getitem__(self, key):
        return self.headers.get(key)
    
    def __setitem__(self, key, value):
        self.headers[key] = str(value)


class HTTPRequest(HTTPMessage):
    def __init__(self, method=None, uri=None):
        super().__init__()

        self.method = method
        self.uri = uri
        self._version = "HTTP/1.1"

    def set_start(self, method, uri):
        self.method = str(method)
        self.uri = uri

    def encode(self):
        result = f"{self.method} {self.uri} {self._version}\r\n"

        for key, value in self.headers.items():
            result += f"{key}: {value}\r\n"

        result += "\r\n"

        return result.encode() + self.body
    
    def parse(message):
        lines = message.split('\r\n')
        start_line = lines[0].split(' ')

        request = HTTPRequest(start_line[0], start_line[1])

        has_end = False

        body = ""
        line_number = 0
        for line in lines[1:]:
            if line == "":
                has_end = True
                break

            # key, value, *other = line.split(":")
            # other = ":".join(other)
            # request[key.strip()] = (value + other).strip()
            request.add_raw_header(line)
            line_number += 1

        has_body = False
        if request["Content-Length"] is not None:
            has_body = True

            # for line in lines[line_number + 1:]:
            #     body += line + "\r\n"

            body = message[message.find('\r\n\r\n') + 4:]

        if has_end and has_body and int(request["Content-Length"]) != len(body):
            has_end = False

        request.set_body(body)
        
        return has_end, request


class HTTPResponse(HTTPMessage):
    def __init__(self, code=None, reason=None):
        super().__init__()
        self._version = "HTTP/1.1"
        self.code = str(code)
        self.reason = reason

    def set_start(self, code, reason):
        self.code = str(code)
        self.reason = reason

    def encode(self):
        result = f"{self._version} {self.code} {self.reason}\r\n"

        for key, value in self.headers.items():
            result += f"{key}: {value}\r\n"

        result += "\r\n"

        return result.encode() + self.body

    def parse(message):
        lines = message.split('\r\n')
        start_line = lines[0].split(' ')

        response = HTTPResponse(start_line[0], start_line[1])

        has_end = False

        body = ""
        line_number = 0
        for line in lines[1:]:
            if line == "":
                has_end = True
                break

            # key, value, *other = line.split(":")
            # other = ":".join(other)
            # response[key.strip()] = (value + other).strip()
            response.add_raw_header(line)
            line_number += 1

        has_body = False
        if response["Content-Length"] is not None:
            has_body = True

            body = message[message.find('\r\n\r\n') + 4:]

            # for line in lines[line_number + 1:]:
            #     body += line + "\r\n"

        if has_end and has_body and int(response["Content-Length"]) != len(body.encode()):
            has_end = False

        # print(body)
        # print(response["Content-Length"])
        # print(len(body.encode()))

        response.set_body(body)
        
        return has_end, response