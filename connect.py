import threading
import socket
from cipher import generatePrivateAndPublicKey, loadReceiverPublicKey, encryptMessage, decryptMessage


# Generate Public and Private Key
my_public_key = generatePrivateAndPublicKey()

# Initialize global variable for peer's public key
peer_public_key = None


# Send message to other PC
def send_message(conn):
    global peer_public_key

    # Send public key first
    try:
        conn.sendall(my_public_key)
        print("Public key sent")
    except (ConnectionResetError, OSError) as e:
        print(f"Error sending public key: {e}")
        return

    while True:
        try:
            message = input("You: ").encode('utf-8')

            # Encrypt message using peer's public key
            if peer_public_key:
                encrypted_message = encryptMessage(
                    message, peer_public_key
                )
                conn.sendall(encrypted_message)
            else:
                print("Waiting for peer's public key....")

        except (ConnectionResetError, OSError) as e:
            print(f"Error sending message: {e}")
            break


# Receive message from other PC
def receive_message(conn):
    global peer_public_key

    while True:
        try:
            if peer_public_key is None:
                peer_public_key_data = conn.recv(2048)

                if peer_public_key_data:
                    peer_public_key = loadReceiverPublicKey(
                        peer_public_key_data
                    )
                    print("Peer's public key received!")
                else:
                    print("Failed to receive peer's public key.")
                    break

            else:
                encryptedMessage = conn.recv(2048)

                if not encryptedMessage:
                    print("Connection closed by peer.")
                    break

                # Decrypt message
                decryptedMessage = decryptMessage(encryptedMessage)
                print(f"Peer: {decryptedMessage.decode('utf-8')}")

        except (ConnectionResetError, OSError) as e:
            print(f"Error receiving message: {e}")
            break


# Start client mode
def start_client_mode(server_ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            print(f"Attempting to connect to {server_ip}:{port}")
            s.connect((server_ip, port))
            print(f"Connected to {server_ip}:{port}")

            # Start thread to send and receive messages
            receive_thread = threading.Thread(
                target=receive_message, args=(s,)
            )
            send_thread = threading.Thread(
                target=send_message, args=(s,)
            )

            receive_thread.start()
            send_thread.start()

            # Keep both threads running
            receive_thread.join()
            send_thread.join()

        except (ConnectionRefusedError, OSError) as e:
            print(f"Failed to connect to server: {e}")


# Start server mode
def start_server_mode(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()

        print(f"Waiting for a connection on {host}:{port}")
        conn, addr = s.accept()
        print(f"Connected by {addr}")

        # Start thread to send and receive messages
        receive_thread = threading.Thread(
            target=receive_message, args=(conn,)
        )
        send_thread = threading.Thread(
            target=send_message, args=(conn,)
        )

        receive_thread.start()
        send_thread.start()

        # Keep both threads running
        receive_thread.join()
        send_thread.join()