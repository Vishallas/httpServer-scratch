import socket
import os

class tcpServer:
    def __init__(self,host='127.0.0.1', port=8888):
        self.host = host
        self.port = port

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        s.bind((self.host,self.port))
        s.listen(5)
        print(f'Listening on {s.getsockname()}')
        while True:
            conn, addr = s.accept()
            print(f'Connected with {addr}')
            data = conn.recv(1024)

            response = self.handle_request(data)
            conn.sendall(response)
            conn.close()

    def handle_request(self,data):
        return data

class httpRequest:
    def __init__(self,data):
        self.method = None        
        self.uri = None
        self.http_version='1.1'

        self.parse(data)

    def parse(self, data):
        line = data.split(b'\r\n')
        line_data = line[0].split(b' ')
        self.method = line_data[0].decode()
        
        if (len(line_data)>1):
            self.uri = line_data[1].decode()
        
        if (len(line_data)>2):
            self.http_version = line_data[2].decode() 

class httpServer(tcpServer):
    Header = {
        'server': 'Scratch_Server',
        'Content-Type': 'text/html',
    }
    
    Status_codes={
        200: 'OK',
        404: 'Not Found',
        501: 'Not Implemented',
    }

    def handle_request(self, data):
        request = httpRequest(data)

        try:
            # print(request.method, type(request.method))
            handler = getattr(self, 'handle_%s'% request.method)
        except AttributeError:
            handler = self.handle_501_handler

        response = handler(request)
        return response

    def handle_GET(self,request):
        uri = 'templates/%s.html' % request.uri.strip('/')
        if os.path.exists(uri):
            response_line = self.response_line(200, request.http_version)
            response_headers = self.response_header()
            with open(uri, 'rb') as body:
                response_body = body.read()
        else:
            response_line = self.response_line(404, request.http_version)
            response_headers = self.response_header()
            response_body = b'<h1>Page not found 401</h1>'
        return self.parse(response_line, response_headers, response_body)

    def handle_501_handler(self,request):
        response_line = self.response_line(501, request.http_version)
        response_headers = self.response_header()
        response_body = b'<h1>Page not implemented 501</h1>'
        return self.parse(response_line, response_headers, response_body)

    def response_line(self, status_code, http_version):
        reason = self.Status_codes[status_code]
        line = '%s %s %s\r\n' % (http_version, status_code,reason)
        return line.encode()
    
    def response_header(self, extra_header=None):
        header_copy = self.Header.copy()
        if extra_header:
            header_copy.update(extra_header)
        header = ''
        for h in header_copy:
            header += '%s: %s\r\n'%(h, header_copy[h])
        return header.encode()

    def parse(self, response_line, response_headers, response_body):
        return b"".join([response_line, response_headers, b'\r\n', response_body])

if __name__ == '__main__':
    server = httpServer()
    server.start()