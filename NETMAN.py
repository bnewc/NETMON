import threading
import time
import socket
import json
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.patch_stdout import patch_stdout
from io_functions import select_from_list
from service_manager import ServiceManager
import queue


# Worker thread function
def monitor_thread(stop_event: threading.Event, name: str, data: dict, print_queue) -> None:
    """
    Check thread
    Runs network check for passed object at object's specified interval
    """
    socket_info = data["socket"]
    ip, port = socket_info["ip"], socket_info["port"]
    checks = data["checks"]

    while not stop_event.is_set():
        # Connect to monitor socket
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        with client_sock:
            # Connect and send check info
            client_sock.setblocking(True)
            try:
                client_sock.connect((ip, port))
            except ConnectionRefusedError:
                print(f"Network monitor service '{name}' is offline. Attempting to reconnect.")
                time.sleep(5)
                continue
            print(f"Connected to service '{name}'")
            client_sock.sendall(bytes(json.dumps(checks), encoding="utf-8"))

            # Until user enters stop command, maintain connection
            client_sock.settimeout(1)
            while not stop_event.is_set():
                try:
                    msg = client_sock.recv(1024)
                except (TimeoutError, ConnectionResetError) as err:
                    if type(err) is TimeoutError:
                        continue
                    else:
                        print(f"Monitoring service '{name}' disconnected. Attempting to reconnect.")
                        break

                if msg:
                    msg = json.loads(msg.decode())
                    print_queue.put(
                        {
                            "time": msg["time"],
                            "name": name,
                            "ip": ip,
                            "port": port,
                            "result": msg["results"]
                        }
                    )
                elif not stop_event.is_set():
                    print(f"Connection to service '{name}' timed out. Attempting to reconnect.")
                    break


def queue_printer(stop_event, print_queue):
    while not stop_event.is_set():
        try:
            data = print_queue.get(timeout=5)
            msg = f"[{data['time']}]: {data['name']} ({data['ip']}:{data['port']}) -- {data['result']}"
            print(msg)
        except queue.Empty:
            continue


# Output status and check for command input
def command_loop() -> None:
    """
    Main function to handle user input and manage threads.
    Uses prompt-toolkit for handling user input with auto-completion and ensures
    the prompt stays at the bottom of the terminal.
    """
    # Event to signal the worker thread to stop
    stop_event: threading.Event = threading.Event()

    # Define services to monitor
    service_manager = ServiceManager()
    config = service_manager.startup()

    # Create a thread for each monitoring service
    sub_threads = []
    print_queue = queue.Queue()
    for name, remote_monitor in config.items():
        sub_thread: threading.Thread = threading.Thread(target=monitor_thread, args=(stop_event, name, remote_monitor, print_queue))
        sub_thread.start()
        sub_threads.append(sub_thread)

    # Create thread for printing messages in queue
    print_thread = threading.Thread(target=queue_printer, args=(stop_event, print_queue))
    print_thread.start()
    sub_threads.append(print_thread)

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
                user_input: str = session.prompt("Enter 'stop' to terminate manager: ")
                if user_input == "stop":
                    print("Monitoring finished\n")
                    is_running = False
    finally:
        # Signal the workers thread to stop and wait for their completion
        stop_event.set()
        for sub_thread in sub_threads:
            sub_thread.join()
        return


def main():
    print("\nNETMAN - Network Manager")
    while True:
        # Begin monitoring and waiting for user commands
        command_loop()

        # Check if user would like to quit
        print("Would you like to monitor a new set of services?")
        selection = select_from_list(["Yes", "No (exit)"])
        if selection in (-1, 0):
            continue
        print("Exiting...") 
        break


if __name__ == "__main__":
    main()
