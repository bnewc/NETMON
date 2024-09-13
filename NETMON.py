import threading
import time
import socket
import sys
import datetime
import json
import queue
from services import *
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.patch_stdout import patch_stdout
from io_functions import select_from_list
from service_monitor import ServiceMonitor


# Worker thread function
def worker(stop_event: threading.Event, check: object, out_queue) -> None:
    """
    Check thread
    Runs network check for passed object at object's specified interval
    """
    while not stop_event.is_set():
        out_queue.put({"time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "results": check.check()})
        micro_interval = check.interval

        # Sleep in 100ms increments until interval is up or stop event set
        # This ensures the thread will terminate within ~100ms of receiving a stop command
        while not stop_event.is_set() and micro_interval > 0:
            time.sleep(0.1)
            micro_interval -= 0.1


def config(stop_event, checks_dict, out_queue, client_sock, server_sock):
    # Define services to monitor
    service_monitor = ServiceMonitor()
    service_monitor.set_checks_from_dict(checks_dict)
    checks = service_monitor.get_checks()

    # Create a thread for each check
    sub_threads = []
    for check in checks:
        worker_thread: threading.Thread = threading.Thread(target=worker, args=(stop_event, check, out_queue))
        worker_thread.start()
        sub_threads.append(worker_thread)

    # Create thread for sending messages in queue
    send_thread = threading.Thread(target=send_queue, args=(stop_event, client_sock, server_sock, out_queue))
    send_thread.start()
    sub_threads.append(send_thread)

    return sub_threads


def send_queue(stop_event, client_sock, server_sock, out_queue):
    while not stop_event.is_set():
        try:
            msg = out_queue.get(timeout=1)
            while not stop_event.is_set():
                try:
                    client_sock.sendall(bytes(json.dumps(msg), encoding="utf-8"))
                    break
                except ConnectionAbortedError:
                    print("Manager service disconnected. Attempting to reconnect...")
                    while not stop_event.is_set():
                        server_sock.settimeout(1)
                        try:
                            client_sock, client_address = server_sock.accept()
                            print(f"Reconnected to manager service at {client_address}")
                        except TimeoutError:
                            continue
        except queue.Empty:
            continue


# Output status and check for command input
def command_loop(port) -> None:
    """
    Main function to handle user input and manage threads.
    Uses prompt-toolkit for handling user input with auto-completion and ensures
    the prompt stays at the bottom of the terminal.
    """
    stop_event: threading.Event = threading.Event()
    maintain = True

    # Event to signal the worker thread to stop
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    with server_sock:
        server_sock.bind(('localhost', port))
        server_sock.listen(1)

        while maintain:
            # Accept client connection
            print("Connecting to manager service...")
            client_sock, client_address = server_sock.accept()
            print(f"Connected to manager at {client_address}")
            with client_sock:
                data = ''
                while True:
                    msg = client_sock.recv(1024)
                    data += msg.decode()
                    if len(msg) < 1024:
                        confirmation = {
                            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "results": "Configuration received! Beginning checks..."
                        }
                        client_sock.sendall(bytes(json.dumps(confirmation), encoding="utf-8"))
                        break
                checks_dict = json.loads(data)
                out_queue = queue.Queue(maxsize=1)
                check_threads = config(stop_event, checks_dict, out_queue, client_sock, server_sock)

                command_completer: WordCompleter = WordCompleter(['stop'], ignore_case=True)

                # Create a prompt session
                session: PromptSession = PromptSession(completer=command_completer)
                is_running: bool = True

                try:
                    with patch_stdout():
                        while is_running:
                            # Using prompt-toolkit for input with auto-completion
                            user_input: str = session.prompt("Enter 'stop' to terminate monitoring: ")
                            if user_input == "stop":
                                print("Monitoring finished\n")
                                is_running, maintain = False, False
                finally:
                    # Signal the workers thread to stop and wait for their completion
                    stop_event.set()
                    for worker_thread in check_threads:
                        worker_thread.join()


def main():
    print("\nNETMON - Network Monitor")
    while True:
        # Begin monitoring and waiting for user commands
        if len(sys.argv) != 2:
            print("Usage: NETMON [port]")
            return
        command_loop(int(sys.argv[1]))

        # Check if user would like to quit
        print("\nDisconnected from manager service. Would you like to reconnect?")
        selection = select_from_list(["Yes", "No (exit)"])
        if selection in (-1, 0): 
            continue
        print("Exiting...")  
        break


if __name__ == "__main__":
    main()
