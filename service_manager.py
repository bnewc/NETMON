from io_functions import *
import os
import json


class ServiceManager:
    """Monitor class to maintain list of checks"""

    def __init__(self):
        self._services = {
            "HTTP": self.add_http_check,
            "HTTPS": self.add_https_check,
            "ICMP": self.add_icmp_check,
            "DNS": self.add_dns_check,
            "NTP": self.add_ntp_check,
            "TCP": self.add_tcp_check,
            "UDP": self.add_udp_check,
            "Echo": self.add_echo_server_check
        }
        self._service_lookup = [service for service in self._services]
        self._service_configs = {}
        self._monitor_config = {}
        self._dns_record_types = [
            "A", "AAAA", "MX", "CNAME", "manual entry"
        ]
        self._monitor_config_path = "./configs/"

    def startup(self):
        """Begin configuration process"""
        while True:
            self.set_config()
            print_config(self._monitor_config)
            self.save_config(self._monitor_config)
            if not get_input_confirmation("Continue managing configuration?"):
                return self._monitor_config

    def get_config(self):
        return self._monitor_config

    def list_monitor_configs(self):
        """Return list of monitor config files in monitor config subdirectory"""
        return [file for file in os.listdir(self._monitor_config_path) if file.endswith(".json")]  

    def load_config(self):
        """Import monitoring configuration file. Default 'def_config.json' """
        configs = self.list_monitor_configs()
        if len(configs) == 0:
            print("No configurations found!\n")
            return False
        print("Select configuration:")
        filename = configs[select_from_list(configs)]

        with open(os.path.join(self._monitor_config_path, filename), 'r') as file:
            self._monitor_config = json.load(file)
        return True

    def save_config(self, config: dict):
        """Save config under filename. Default: 'def_config.json' """
        while True:
            if not get_input_confirmation("Would you like to save this configuration?"):
                return
            filename = get_input_manual("filename")
            if filename in self.list_monitor_configs():
                if get_input_confirmation(f"A file named {filename} already exists. Overwrite?"):
                    break
            else:
                if get_input_confirmation(f"Save configuration as {filename}?"):
                    break
        with open(os.path.join(self._monitor_config_path, filename), 'w') as file:
            json.dump(config, file)
        print("File saved!")

    def set_config(self):
        # Choose an option
        while True:
            options = [
                ("Load a configuration", self.load_config),
                ("Input a new configuration", self.manually_configure)
            ]
            # Call function for selected operation
            config = options[select_from_list([x[0] for x in options])][1]()
            if config:
                return

    def manually_configure(self):
        # Configure checks
        checks = self._manually_configure_checks()
        # Configure monitoring services
        monitors = self._manually_configure_monitors()

        print("Which check should be sent to each monitor?")
        check_indices = [x for x in checks]
        for monitor in monitors:
            print(monitor)
            # Select check to send to monitor
            self._monitor_config[monitor] = {
                "socket": monitors[monitor],
                "checks": checks[check_indices[select_from_list(check_indices)]]
            }
        return True

    def _manually_configure_monitors(self):
        """
        Create dictionary of monitor to run service checks

        :returns:   dictionary of monitors
        """
        print("Configuring monitoring services...")
        config = {}
        while True:
            name = get_input_manual("monitoring service name")
            ip = get_input_manual("host's IP address")
            port = get_input_port_number()

            config[name] = {"ip": ip, "port": port}

            # continue adding?
            if not get_input_confirmation("Add another monitor?"):
                return config if config != {} else None

    def _manually_configure_checks(self):
        checks = {}
        while True:
            name, check = self.create_check_set()
            checks[name] = check
            if not get_input_confirmation("Add another set of checks?"):
                break
        return checks

    def create_check_set(self) -> (str, dict):
        """
        Create list of services to monitor

        :returns:   name, dictionary of services
        """
        name = get_input_manual("name for set of checks")
        print("Select a service to monitor or press Enter to finish.")
        check_set = {}
        while True:
            selection = select_from_list(self._service_lookup)

            # call the respective add method
            service_name = self._service_lookup[selection]
            service = self._services[service_name]
            print(f"Adding {service_name} check")
            service(check_set)
            if not get_input_confirmation("Add another service?"):
                return name, check_set if check_set != {} else None

    def add_check_config(self, config, check, check_type):
        if check_type not in config:
            config[check_type] = []
        config[check_type].append(check)   

    def _handle_add_http(self, config, *, https: bool = False):
        """
        Handles addition of both HTTP and HTTPS checks

        :param https:   is service HTTPS? True if so. False by default
        :returns:       True if added, else False
        """
        # Get URL
        url = get_input_manual("URL", back=True)
        if url is None: 
            return False
        check = {"url": url}

        if https:
            check_type = "HTTPS"
            check["timeout"] = get_input_timeout(5)
        else:
            check_type = "HTTP"
        check["interval"] = get_input_interval()

        self.add_check_config(config, check, check_type)
        return True

    def add_http_check(self, config):
        """
        Add HTTP service check

        :returns:   True if added, else False
        """
        return self._handle_add_http(config)

    def add_https_check(self, config):
        """
        Add HTTPS service check

        :returns:   True if added, else False
        """
        return self._handle_add_http(config, https=True)

    def add_icmp_check(self, config):
        """
        Add ICMP service check

        :returns:   True if added, else False
        """
        # Get host
        host = get_input_manual("hostname or IP address", back=True)
        if host is None:
            return False  
        check = {
            "host": host,
            "ttl": get_input_ttl(64),
            "timeout": get_input_timeout(1),
            "sequence_number": get_input_sequeunce_number(1),
            "interval": get_input_interval()
        }

        # Get other parameters

        # Add check to config
        self.add_check_config(config, check, "ICMP")
        return True

    def add_dns_check(self, config):
        """
        Add DNS service check

        :returns:   True if added, else False
        """
        # Get server and query names
        server = get_input_manual("DNS server name or IP address", back=True)
        if server is None:
            return False
        check = {"server": server, "query": get_input_manual("domain name to query")}

        # Get DNS record type
        print("Input DNS record type")
        print("If unsure, A is recommended")
        while True:
            selection = select_from_list(self._dns_record_types)
            if selection != -1:
                break
        if self._dns_record_types[selection] == "manual entry":     # manual entry
            check["record_type"] = get_input_manual("record type")
        else:
            check["record_type"] = self._dns_record_types[selection]

        # Get check interval
        check["interval"] = get_input_interval()

        self.add_check_config(config, check, "DNS")
        return True

    def add_ntp_check(self, config):
        """
        Add NTP service check

        :returns:   True if added, else False
        """
        # Get parameters
        server = get_input_manual("hostname or IP address", back=True)
        if server is None:
            return False
        check = {"server": server, "interval": get_input_interval()}

        self.add_check_config(config, check, "NTP")
        return True

    def _handle_transport_check(self, config, protocol: str):
        """
        Handles addition of both TCP and UDP service checks

        :returns:   True if added, else False
        """
        # Get IP
        ip = get_input_manual("IP address", back=True)
        if ip is None:
            return False

        check = {
            "ip_address": ip, 
            "port": get_input_port_number()
        }

        # Is protocol TCP or UDP?
        if protocol == "UDP":
            check["timeout"] = get_input_timeout(3)    # if UDP, get timeout

        check["interval"] = get_input_interval()

        self.add_check_config(config, check, protocol)
        return True

    def add_tcp_check(self, config):
        """
        Add TCP service check

        :returns:   True if added, else False
        """
        return self._handle_transport_check(config, "TCP")

    def add_udp_check(self, config):
        """
        Add UDP service check

        :returns:   True if added, else False
        """
        return self._handle_transport_check(config, "UDP")

    def add_echo_server_check(self, config):
        """
        Add check for echo server

        :returns:   True if added, else False
        """
        if not get_input_confirmation(f"You've input: echo server. Is that correct?"):
            return False
        check = {
            "ip_address": 'localhost',
            "port": get_input_port_number(),
            "interval": get_input_interval()
        }

        self.add_check_config(config, check, "Echo")
        return True


def main():
    manager = ServiceManager()
    manager.startup()


if __name__ == '__main__':
    main()
