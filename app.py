from connect import start_client_mode, start_server_mode


if __name__ == "__main__":
    mode = input("Enter mode (server/client): ").strip().lower()

    if mode == "server":
        host = "0.0.0.0" # Use local IP address
        port = 65432

        start_server_mode(host, port)

    elif mode == "client":
        server_ip = input("Enter server IP address: ").strip()
        port = 65432

        start_client_mode(server_ip, port)

    else:
        print("Invalid mode! Please enter server or client")