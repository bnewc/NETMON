# NETMON

A distributed app for running network checks on remote systems. 

Using the `NETMAN` manager service, 
configure checks for network services like HTTP/S, DNS, TCP, and UDP at selected intervals.


Run `NETMON` monitor services on remote hosts to receive and run checks from managers.

# Usage

## Local Host
- Launch `app/NETMAN.py`
- Follow the instructions to create or load a JSON configuration. 
	- If you save a config file, be sure to append .json to the name. 
	- Configs are stored in the 'configs' folder.
- Once you've selected a configuration, select the option to begin testing.
- To stop displaying results, enter command "stop".

## Remote Hosts
- Launch an instance of `app/NETMON.py [port]` with port corresponding to the specified port number in the selected `NETMAN` config file.
- To stop running checks, enter command "stop".