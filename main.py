#!/usr/bin/python3.5
# coding=utf-8

import socket
import os
import time
import sys

def send_answer(conn, status="200 OK", typ="text/plain; charset=utf-8", data=""):
	data = data.encode("utf-8")
	conn.send(b"HTTP/1.1 " + status.encode("utf-8") + b"\r\n")
	conn.send(b"Server: simplehttp\r\n")
	conn.send(b"Connection: close\r\n")
	conn.send(b"Content-Type: " + typ.encode("utf-8") + b"\r\n")
	conn.send(b"Content-Length: " + bytes(len(data)) + b"\r\n")
	conn.send(b"\r\n") # после пустой строки в HTTP начинаются данные
	conn.send(data)


def parse_data(conn, addr):
	data = b""
	while not b"\r\n" in data:
		tmp = conn.recv(1024)
		if not tmp:
			break
		else:
			data += tmp
	if not data:
		return
	udata = data.decode("utf-8")
	udata = udata.split("\r\n", 1)[0]
	method, address, protocol = udata.split(" ", 2)
	print("%s - - [%s] \"%s\""% (addr[0], time.strftime("%d/%b/%G %H:%M:%S"), udata))

	content = os.listdir(path='.'+address)

	if method != "GET" and len(content) == 0:
		send_answer(conn, "404 Not Found", data = "404 Not Found")
		return

	answer = "<!DOCTYPE html>"
	answer += "<html><head><title>Directory listing for</title></head><body>"
	answer += "<h1>Directory listing for {0:s}</h1><hr><ul>".format(address)
	for elem in content:
		answer += "<li><a href=\"{0:s}\">{0:s}</a></li>".format(elem)
	answer += "</ul><hr></body></html>"

	send_answer(conn, typ="text/html; charset=utf-8", data=answer)


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


host_port = get_port(sys.argv, 8000)
host_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
#hostname = socket.gethostname()
host_sock.bind(('', host_port))
print("Serving HTTP on %s port %d ..."% sock.getsockname())
#listens for up to 10 connections
host_sock.listen(10)
try:
	while True:
		client_sock,client_addr = host_sock.accept()
		try:
			parse_data(client_sock, client_addr)
		except:
			send_answer(client_sock, "500 Internal Server Error", data="500 Internal Server Error")
		finally:
			client_sock.close()
except KeyboardInterrupt:
	print("\nKeyboard interrupt received, exiting.")
finally:
	host_sock.close()
