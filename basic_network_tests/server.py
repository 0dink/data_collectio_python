import socket

def main():
    try: 
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', 8080))
        server_socket.listen(5)
        print("listening on port 8080")

        conn, addr = server_socket.accept()
        print(f"Connection from {addr}")

        data = conn.recv(1024).decode()
        print(f"Received: {data}")

        conn.close()
        server_socket.close()
    except Exception as e:
        print(f"server error: {e}")
if __name__ == "__main__":
    main()