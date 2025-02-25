import socket

def read_ip():
    try:
        return open("../inputs/server_ip.txt", "r").readline().strip()
    except Exception as e:
        print(f"Error reading IP: {e}")
        exit(1)

def main():

    server_ip = read_ip()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, 8080))
    
    message = "Hello, World!"
    client_socket.sendall(message.encode())
    
    client_socket.close()

if __name__ == "__main__":
    main()