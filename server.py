# TODO: import modules
import os
import socket

# TODO: set constants
IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 0.1
MAX_LENGTH_SIZE = 1024
FIXED_RESPONSE = "HTTP/1.1 200 OK\r\n"
DEFAULT_URL = 'index.html'
WEBROOT = "C:/Networks/webroot/"
REDIRECTION_DICTIONARY = {
    "uploads/screen.jpg" : "imgs/screen.jpg"
}
RESTRICTED_LIST = ["uploads/images/screen.jpg", "mime.csv"]


def get_file_data(filename):
    """ Get data from file """
    data = open(filename, 'rb').read()
    return data


def handle_client_request(resource, client_socket):
    """ Check the required resource, generate proper HTTP response and send to client"""
    # TODO : add code that given a resource (URL and parameters) generates the proper response
    try:
        if resource == '':
            url = DEFAULT_URL
        else:
            url = resource
        print(url)
        filename = WEBROOT + url
        # TODO: check if URL had been redirected, not available or other error code. For example:
        if url in REDIRECTION_DICTIONARY:
            # TODO: send 302 redirection response
            response = "HTTP/1.1 302 Found\r\nLocation: " + [value for key, value in REDIRECTION_DICTIONARY.items() if key == url][0]
            response += "\r\n\r\n"
            client_socket.send(response.encode())
            url = REDIRECTION_DICTIONARY[url]
            filename = WEBROOT + url
        if not os.path.isfile(filename):
            client_socket.send("HTTP/1.1 404 Not Found\r\n\r\n".encode())
            return
        if url in RESTRICTED_LIST:
            client_socket.send("HTTP/1.1 403 Forbidden\r\n\r\n".encode())
            return
        # TODO: extract requested file type from URL (html, jpg etc)
        filetype = filename.split('.')[-1]
        if filetype == 'html':
            http_header = "Content-Type: text/html; charset=utf-8"  # TODO: generate proper HTTP header
        elif filetype == 'jpg':
            http_header = "Content-Type: image/jpg"  # TODO: generate proper jpg header
        elif filetype == 'jpeg':
            http_header = "Content-Type: image/jpeg"  # TODO: generate proper jpeg header
        elif filetype == 'css':
            http_header = "Content-Type: text/css"  # TODO: generate proper css header
        elif filetype == 'js':
            http_header = "Content-Type: application/javascript"  # TODO: generate proper js header
        elif filetype == 'gif':
            http_header = "Content-Type: image/gif"  # TODO: generate proper gif header
        elif filetype == 'ico':
            http_header = "Content-Type: image/x-icon"  # TODO: generate proper ico header
        else:
            client_socket.send("HTTP/1.1 500 Internal Server Error\r\n\r\n".encode())
        # TODO: handle all other headers
        http_header += "Content-Length:" + str(os.path.getsize(filename)) + "\r\n\r\n"

        # TODO: read the data from the file
        data = get_file_data(filename)
        http_response = FIXED_RESPONSE.encode() + http_header.encode() + data
        client_socket.send(http_response)
    except FileNotFoundError:
        print(url + "not found")
        client_socket.send("HTTP/1.1 500 Internal Server Error\r\n\r\n".encode())


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and the requested URL
    """
    # TODO: write function
    # GET / HTTP/1.1\r\n
    request = request.split(' ')
    method = request[0]
    url = request[1]
    version_and_new_line = request[2]
    if method != "GET" or not version_and_new_line.startswith("HTTP/1.1\r\n") or url[0] != '/':
        return False, "ERROR"
    return True, url[1:]


def handle_client(client_socket):
    """ Handles client requests: verifies client's requests are legal HTTP, calls function to handle the requests """
    print('Client connected')
    while True:
        # TODO: insert code that receives client request
        client_request = client_socket.recv(MAX_LENGTH_SIZE).decode()
        # ...
        valid_http, resource = validate_http_request(client_request)
        if valid_http:
            print('Got a valid HTTP request')
            handle_client_request(resource, client_socket)
            break
        else:
            print('Error: Not a valid HTTP request')
            client_socket.send("HTTP/1.1 500 Internal Server Error\r\n\r\n".encode())
            break
    print('Closing connection')
    client_socket.close()


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    print("Listening for connections on port {}".format(PORT))

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)
        handle_client(client_socket)


if __name__ == "__main__":
    # Call the main handler function
    main()
