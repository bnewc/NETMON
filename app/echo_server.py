# Citation for the following program:
# Date: 01/28/2024
# Written with reference to:
# Source URL: https://docs.python.org/3/howto/sockets.html
# Source URL: https://docs.python.org/3/library/socket.html

import socket
import threading
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.patch_stdout import patch_stdout


# Worker thread function
def worker(stop_event: threading.Event) -> None:
    """
    Open server socket and echo messages back
    """
    # Set up server socket
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.settimeout(3)
    with server_sock:
        server_sock.bind(('localhost', 45446))
        server_sock.listen()

        while not stop_event.is_set():
            # Accept client connection
            try:
                # Nonblocking accept call
                client_sock, client_address = server_sock.accept()
                with client_sock:

                    # Recieve and echo back messages from client until connection is closed
                    while True:
                        client_msg = client_sock.recv(1024)
                        if not client_msg:
                            break
                        client_sock.sendall(client_msg)

            # If accept call times out, thread stop event will be checked
            except TimeoutError:
                pass


# Output status and check for command input
def command_loop() -> None:
    """
    Main function to handle user input and manage threads.
    Uses prompt-toolkit for handling user input with auto-completion and ensures
    the prompt stays at the bottom of the terminal.
    """
    # Event to signal the worker thread to stop
    stop_event: threading.Event = threading.Event()

    # Create a thread for the server socket
    worker_thread: threading.Thread = threading.Thread(target=worker, args=(stop_event,))
    worker_thread.start()

    # Command completer for auto-completion
    # This is where you will add new auto-complete commands
    command_completer: WordCompleter = WordCompleter(['stop'], ignore_case=True)

    # Create a prompt session
    session: PromptSession = PromptSession(completer=command_completer)

    # Variable to control the main loop
    is_running: bool = True

    try:
        with patch_stdout():
            while is_running:
                # Using prompt-toolkit for input with auto-completion
                user_input: str = session.prompt("Enter 'stop' to kill server: ")
                if user_input == "stop":
                    print("Exiting...\n")
                    is_running = False
    finally:
        # Signal the workers thread to stop and wait for its completion
        stop_event.set()
        worker_thread.join()
        return


def main():
    # Begin monitoring and waiting for user commands
    print("Echo server running...")
    command_loop()


if __name__ == "__main__":
    main()
