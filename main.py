#!/usr/bin/python3.5

import socket
import os
import time
import sys
import mimetypes
from http import HTTPStatus

def error_page(err_code='404', mess=' '):
    err_page = "<!DOCTYPE html><html><head>"
    err_page += "<meta http-equiv=\"Content-Type\" content=\"text/html;charset=utf-8\">"
    err_page += "<title>Error response</title></head><body>"
    err_page += "<h1>Error response</h1>"
    err_page += "<p>Error code: {:d}</p>".format(err_code)
    err_page += "<p>Message: {:s}.</p>".format(mess)
    err_page += "</body></html>"
    return err_page

def send_answer(conn, status="200 OK", typ="text/plain; charset=utf-8", data=""):
	if "text" in typ:
		data = data.encode("utf-8")
	conn.send(b"HTTP/1.1 " + status.encode("utf-8") + b"\r\n")
	conn.send(b"Server: simplehttp\r\n")
	conn.send(b"Connection: close\r\n")
	conn.send(b"Content-Type: " + typ.encode("utf-8") + b"\r\n")
	conn.send(b"Content-Length: " + bytes(len(data)) + b"\r\n")
	conn.send(b"\r\n")
	conn.send(data)

def file_manager(address):
	try:
		content = os.listdir(path='.' + address)
	except OSError:
		return error_page(HTTPStatus.NOT_FOUND, "No permission to list directory")
	content.sort(key = lambda a: a.lower())
	for index in "index.html", "index.htm":
		if index in content:
			with open('.' + address + index) as page:
				return page.read()
	result = "<!DOCTYPE html>"
	result += "<html><head><title>Directory listing for {0:s}</title></head><body>"
	result += "<h1>Directory listing for {0:s}</h1><hr><ul>".format(address)
	for elem in content:
		if os.path.isdir('.' + address + elem):
			elem += '/'
		result += "<li><a href=\"{0:s}\">{0:s}</a></li>".format(elem)
	result += "</ul><hr></body></html>"
	return result

def parse_data(client_sock, client_addr):
	state = 200
	data = b""
	while not b"\r\n" in data:
		tmp = client_sock.recv(1024)
		if not tmp:
			break
		else:
			data += tmp
	if not data:
		return
	udata = data.decode("utf-8")
	udata = udata.split("\r\n", 1)[0]
	method, address, protocol = udata.split(" ", 2)
	if method == "GET":
		if os.path.isdir('.' + address):
			answer = file_manager(address)
			typ = "text/html; charset=utf-8"
		else:
			typ = extensions_map[os.path.splitext(address)[1]]
			try:
				if "text" in typ:
					typ += "; charset=utf-8"
					file = open('.' + address)
				else:
					file = open('.' + address, 'rb')
				answer = file.read()
				file.close()
			except OSError:
				typ = "text/html; charset=utf-8"
				state = HTTPStatus.NOT_FOUND
				answer = error_page(state, "Error opening file")
	else:
		state = HTTPStatus.NOT_FOUND
		answer = error_page(state, "File not found")
	print("%s - - [%s] \"%s\" %d -"% (client_addr[0], time.strftime("%d/%b/%G %H:%M:%S"), udata, state))
	send_answer(client_sock, typ=typ, data=answer)


def get_port(argv, result):
	if len(argv) == 2:
		try:
			result = int(argv[1])
			if result not in range(1024,65536):
				print("Port out of range!")
				raise SystemExit
		except:
			print("Incorrect input")
			raise
	return result

mimetypes.init()
extensions_map = mimetypes.types_map.copy()
extensions_map.update({
	'': 'application/octet-stream',
	'.py': 'text/plain',
	'.c': 'text/plain',
	'.h': 'text/plain'
	})
host_port = get_port(sys.argv, 8000)
host_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
host_sock.bind(('', host_port))
print("Serving HTTP on %s port %d ..."% host_sock.getsockname())
host_sock.listen(10)
try:
	while True:
		client_sock,client_addr = host_sock.accept()
		try:
			parse_data(client_sock, client_addr)
		except:
			send_answer(client_sock, "500 Internal Server Error", data="500 Internal Server Error")
			raise
		finally:
			client_sock.close()
except KeyboardInterrupt:
	print("\nKeyboard interrupt received, exiting.")
finally:
	host_sock.close()
