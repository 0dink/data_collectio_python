import socket

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 8080))
    server_socket.listen(5)

    conn, addr = server_socket.accept()
    print(f"Connection from {addr}")

    data = conn.recv(1024).decode()
    print(f"Received: {data}")

    conn.close()
    server_socket.close()

if __name__ == "__main__":
    main()