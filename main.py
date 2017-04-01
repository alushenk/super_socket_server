#!/usr/bin/python3.5

import socket

def send_answer(conn, status="200 OK", typ="text/plain; charset=utf-8", data=""):
	data = data.encode("utf-8")
	conn.send(b"HTTP/1.1 " + status.encode("utf-8") + b"\r\n")
	conn.send(b"Server: simplehttp\r\n")
	conn.send(b"Connection: close\r\n")
	conn.send(b"Content-Type: " + typ.encode("utf-8") + b"\r\n")
	conn.send(b"Content-Length: " + bytes(len(data)) + b"\r\n")
	conn.send(b"\r\n")# после пустой строки в HTTP начинаются данные
	conn.send(data)


def parse_data(conn, addr):
	data = b""
	while not b"\r\n" in data:
		#receiving 1024 bytes from 
		tmp = conn.recv(1024)
		if not tmp:
			break
		else:
			data += tmp
	if not data:
		return
	#decoding data into utf-8
	udata = data.decode("utf-8")
	#see what we receive
	print("Data: %s"% udata.split("\r\n", 1)[0])
	answer = "Hello! {0:s}".format(str(connections_count))
	send_answer(conn, typ="text/html; charset=utf-8", data=answer)


"""
тут часть парсинга 
"""

#create socket
sock = socket.socket()
#socket binded to all hosts
sock.bind(("", 8000))
#listens for up to 10 connections
sock.listen(10)
connections_count = 0
try:
	while True:
		#accepting connections. accept() waits for incoming connection and returns
		#binded socket(conn) and IP address of client(addr)
		conn,addr = sock.accept()
		print("New connection from %s"%addr[0])
		try:
			parse_data(conn, addr)
		except:
			send_answer(conn, "500 Internal Server Error", data="Ошибка")
		finally:
			# так при любой ошибке
			# сокет закроем корректно
			conn.close()
			connections_count += 1
finally:
	sock.close()