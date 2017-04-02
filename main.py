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

	"""
	тут надо пропарсить udata.

	if method != "GET" or address 	(не находится в множестве возможных страниц. 
									мона попробовать к нему обратиться, и если лажа вернуть фолс):
	    send_answer(conn, "404 Not Found", data="Не найдено")
	    return

	папка - зайти в нее и вернуть список файлов(и директорий) из нутри
	файл - отобразить содержание/вернуть сам файл для скачивания(опционально, добавить ссылки в интерфейс)
	"""
	content = os.listdir(path='.')
	content.append('')
	udata = udata.split("\r\n", 1)[0]
	method, address, protocol = udata.split(" ", 2)
	print("%s - - [%s] \"%s\""% (addr[0], time.strftime("%d/%b/%G %H:%M:%S"), udata))

	print(address)
	if method != "GET" or address[1:] not in content:
		send_answer(conn, "404 Not Found", data = "404 Not Found")
		return

	answer = "<!DOCTYPE html>"
	answer += "<html><head><title>Directory listing for</title></head><body>"
	answer += "<h1>Directory listing for /</h1><hr>"
	answer += "<h1>Hello! {0:s}</h1><ul>".format(str(connections_count))

	for elem in content:
		answer += "<li><a href=\"{0:s}\">{0:s}</a></li>".format(elem)

	answer += "</ul><hr></body></html>"


	send_answer(conn, typ="text/html; charset=utf-8", data=answer)


if len(sys.argv) == 2:
	try:
		port = int(sys.argv[1])
		if port not in range(1024,65536):
			print("Port out of range!")
			raise SystemExit
	except:
		print("Incorrect input")
		raise
else:
	# в оригинале сделано красивее, там порт это дефолтный параметр функции.
	port = 8000


#create socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
host = socket.gethostname() # Get local machine name. можно прописать просто '', тогда будет дефолтный 127.0.0.1 (Localhost)
#myhost = os.uname()[1] #альтернатива строке сверху
#socket binded to all hosts
sock.bind(('', port))
print("Serving HTTP on %s port %d ..."% sock.getsockname())
#listens for up to 10 connections
sock.listen(10)
connections_count = 0
try:
	while True:
		#accepting connections. accept() waits for incoming connection and returns
		#binded socket(conn) and IP address of client(addr)
		conn,addr = sock.accept()
		try:
			parse_data(conn, addr)
		except:
			send_answer(conn, "500 Internal Server Error", data="Error")
		finally:
			conn.close()
			connections_count += 1
except KeyboardInterrupt:
	print("\nKeyboard interrupt received, exiting.")
finally:
	#print ('-' * 50)
	sock.close()
