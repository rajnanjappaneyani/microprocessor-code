import socket

HOST = "host.docker.internal"
PORT = 80  # change to 8080 if host listens on 8080

x = "(a,b,s)\n"

with socket.create_connection((HOST, PORT), timeout=5) as s:
    s.sendall(x.encode("utf-8"))
