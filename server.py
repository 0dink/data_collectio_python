import socket

from video_utils import send_receive_and_save

def main():
    # Initialize server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_socket.bind(('0.0.0.0', 8080))
    server_socket.listen(10)
    print("Server listening on port 8080...")

    # Accept a client connection
    client_socket, client_address = server_socket.accept()
    print(f"Connection established with {client_address}")

    send_receive_and_save(client_socket, 30, "Server")

    client_socket.close()
    server_socket.close()

if __name__ == "__main__":
    main()