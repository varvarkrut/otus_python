import tcp_server
import datetime
from urllib.parse import unquote
BUFFER_SIZE = 1024
SUPPORTED_HTTP_VERSIONS = ['HTTP/1.1', 'HTTP/1.0']
HTTP_SEPARATOR = '\r\n\r\n'

OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
NOT_ALLOWED = 405

available_methods = ['GET', 'HEAD']
response_codes = {
    200: 'OK',
    400: 'Bad Request',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed'
}


class HTTPServer(tcp_server.TCPServer):
    def __init__(self, host, port, document_root=None):
        super().__init__(host, port)
        self.response_code = OK
        self.response_headers = None
        self.request_headers = None
        self.document_root = document_root or "./"
        self.content = None
        self.basic_http_versoin = 'HTTP/1.1'

    def handle_client_connection(self, client_socket):
        while True:
            request = client_socket.recv(BUFFER_SIZE)
            if HTTP_SEPARATOR.encode() in request or not request:
                break
            print(f'Received {request}')
        request = self._parse_request(request)
        response = self._handle_request(request)
        client_socket.send(response)
        client_socket.close()

    def _parse_request(self, request):
        request = request.decode('utf-8')
        request = request.split('\r\n')
        request = request[0].split(' ')
        if not request or len(request) != 3:
            self.response_code = BAD_REQUEST
            return self.handle_unknown_request()
        return request

    def _handle_request(self, request):
        method, path, protocol = request
        self.path = path
        if protocol not in SUPPORTED_HTTP_VERSIONS:
            self.response_code = NOT_ALLOWED
            return self.handle_unknown_request()
        if protocol == 'HTTP/1.0':
            self.basic_http_versoin = 'HTTP/1.0'
        match method:
            case 'GET':
                return self._handle_get(path)
            case 'HEAD':
                return self._handle_head(path)
            case _:
                self.response_code = NOT_ALLOWED
                return self.handle_unknown_request()

    def _handle_head(self, path):
        # check whether query string is present
        if '?' in path:
            path = path.split('?')[0]
        # check whether path ends with '/'
        if path.endswith('/'):
            path += 'index.html'
        if path.startswith('/'):
            path = path[1:]
        body = self._handle_get_file(path)
        headers = self._get_headers()
        response = f'{self.basic_http_versoin} {self.response_code} {response_codes[self.response_code]}\r\n{headers}\r\n'.encode()
        return response

    def _handle_get(self, path):
        # check whether query string is present
        if '?' in path:
            path = path.split('?')[0]
        # check whether path ends with '/'
        if path.endswith('/'):
            path += 'index.html'
        if path.startswith('/'):
            path = path[1:]

        # handle white spaces in path

        body = self._handle_get_file(path)
        headers = self._get_headers()
        response = f'{self.basic_http_versoin} {self.response_code} {response_codes[self.response_code]} \r\n{headers}\r\n{body}'.encode()
        return response

    def _handle_get_file(self, path):
        # handle url encoded path
        path = unquote(path)
        # avoid path traversal
        if '../' in path:
            self.response_code = FORBIDDEN
            return self.content
        try:
            # check whether file binary or text
            if path.endswith('.jpg') or path.endswith('.png') or path.endswith('.gif') or path.endswith('.swf') or path.endswith('.ico')\
                    or path.endswith('jpeg'):
                with open(self.document_root + path, 'rb') as f:
                    self.content = f.read()
                    self.response_code = OK
                    return self.content

            with open(self.document_root + path, 'r') as f:
                self.content = f.read()
                self.response_code = OK
                return self.content
        except FileNotFoundError:
            self.response_code = NOT_FOUND
            self.content = ""
            return self.content
        except NotADirectoryError:
            self.response_code = NOT_FOUND
            self.content = ""
            return self.content

    def _calculate_content_length(self, content):
        try:
            return len(content.encode('utf-8'))
        except Exception:
            return len(content)

    def _get_date(self):
        return datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')

    def _get_content_type(self, path):
        if path.endswith('.html'):
            return 'text/html'
        elif path.endswith('.css'):
            return 'text/css'
        elif path.endswith('.js'):
            return 'application/javascript'
        elif path.endswith('.jpg') or path.endswith('.jpeg'):
            return 'image/jpeg'
        elif path.endswith('.png'):
            return 'image/png'
        elif path.endswith('.gif'):
            return 'image/gif'
        elif path.endswith('.swf'):
            return 'application/x-shockwave-flash'
        else:
            return 'text/plain'

    def _get_server_info(self):
        return 'Python/3.10 (MacOS)'

    def _get_connection(self):
        return 'close'

    def _get_headers(self):
        headers = {
            'Content-Type': self._get_content_type(self.path) if self.content else '',
            'Content-Length': self._calculate_content_length(self.content) if self.content else 0,
            'Date': self._get_date(),
            'Server': self._get_server_info(),
            'Connection': self._get_connection()
        }

        headers_string = ''.join(
            f'{key}: {value}' + '\r\n' for key, value in headers.items()
        )
        return headers_string

    def handle_unknown_request(self):
        headers = self._get_headers()
        body = self.content
        response = f'{self.basic_http_versoin} {self.response_code} {response_codes[self.response_code]}\r\n{headers}\r\n{body}'.encode()
        return response




if __name__ == '__main__':
    server = HTTPServer('127.0.0.1', 8090)
    server.serve_forever()
