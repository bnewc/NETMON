from network_monitoring_functions import *

default_interval = 5        # seconds
max_interval = 600          # seconds
max_timeout = 300           # seconds
max_ttl = 500
max_16b = 65535


class Service:
    """Simple network service parent class"""
    def __init__(self):
        self.interval = default_interval    # default check interval

    def get_interval(self):
        return self.interval


class HTTP(Service):
    """HTTP service class"""
    def __init__(self):
        self.url = None
        self.service_type = "HTTP"
        super().__init__()

    def check(self) -> str:
        """
        Run HTTP check on stored URL

        :returns:   status of check
        """
        # Add http protocol to URL
        expanded_url = self.url
        if self.url[:7] != "http://":
            expanded_url = f"http://{self.url}"

        # Check URL
        try:
            response = check_server_http(expanded_url)
            if response[0]:
                # Check successful
                return f"HTTP check -- {expanded_url} -- Server is up -- Status: {response[1]}"
            # Check failed
            return f"HTTP check -- {expanded_url} -- Server unreachable"
        except Exception as e:
            return f"HTTP check -- {expanded_url} -- Error: {e}"


class HTTPS(HTTP):
    """HTTPS service class"""
    def __init__(self):
        self.timeout = 5
        self.service_type = "HTTPS"
        super().__init__()

    def check(self) -> str:
        """
        Run HTTPS check on stored URL

        :returns:   status of check
        """
        # Add https protocol
        expanded_url = self.url
        if self.url[:8] != "https://":
            expanded_url = f"https://{self.url}"

        # Check URL
        try:
            response = check_server_https(expanded_url, self.timeout)
            if response[0]:
                # Check successful
                return f"HTTPS check -- {expanded_url} -- Server is up -- Status: {response[1]}"
            # Check failed
            return f"HTTPS check -- {expanded_url} -- Server unreachable -- {response[2]}."
        except Exception as e:
            return f"HTTPS check -- {expanded_url} -- Error: {e}."


class ICMP(Service):
    """HTTPS service class"""
    def __init__(self):
        self.host = None
        self.service_type = "ICMP"
        self.ttl = 64
        self.timeout = 1
        self.sequence_number = 1
        super().__init__()

    def check(self) -> str:
        """
        Run ICMP check on stored host

        :returns:   status of check
        """
        try:
            response = ping(self.host, self.ttl, self.timeout, self.sequence_number)
            if response[1] is None:
                if response[0] is None:
                    # No response
                    return f"ICMP check -- {self.host} -- no response!"
                # Timeout
                return f"ICMP check -- {self.host} -- request timed out!"
            # Check successful
            return f"ICMP check -- {self.host} -- reply from {response[0]} received in {response[1]}ms"
        except Exception as e:
            return f"ICMP check -- {self.host} -- Error: {e}"


class NTP(Service):
    """NTP service class"""
    def __init__(self):
        self.server = None
        self.service_type = "NTP"
        super().__init__()

    def check(self) -> str:
        """
        Run NTP check on stored server

        :returns:   status of check
        """
        try:
            response = check_ntp_server(self.server)
            if response[0]:
                # Check successful
                return f"NTP check -- {self.server} -- Server is up -- Current time: {response[1]}"
            # Check failed
            return f"NTP check -- {self.server} -- Server is unreachable"
        except Exception as e:
            return f"NTP check -- {self.server} -- Error: {e}"


class DNS(NTP):
    """DNS service class"""
    def __init__(self):
        self.service_type = "DNS"
        self.query = None
        self.record_type = None
        super().__init__()

    def check(self) -> str:
        """
        Run DNS check on stored server using stored query and record type

        :returns:   status of check   
        """
        try:
            response = check_dns_server_status(self.server, self.query, self.record_type)
            if response[0]:
                # Check successful
                return f"DNS check -- {self.server} -- Server is up -- {self.query} resolved to {response[1][0]}"
            # Check failed
            return f"DNS check -- {self.server} -- Could not resolve {self.query}: {response[1]}"
        except Exception as e:
            return f"DNS check -- {self.server} -- Error: {e}"


class TCP(Service):
    """TCP service class"""
    def __init__(self):
        self.service_type = "TCP"
        self.ip_address = None
        self.port = None
        super().__init__()

    def check(self) -> str:
        """
        Run TCP check on stored IP and port number

        :returns:   status of check
        """
        try:
            response = check_tcp_port(self.ip_address, self.port)
            return f"TCP check -- {response[1]}"
        except Exception as e:
            return f"TCP check -- {self.ip_address}:{self.port} -- Error: {e}"


class UDP(TCP):
    """UDP service class"""
    def __init__(self):
        self.service_type = "UDP"
        self.timeout = 3
        super().__init__()

    def check(self) -> str:
        """
        Run UDP check on stored IP and port number

        :returns:   status of check
        """
        try:
            response = check_udp_port(self.ip_address, self.port, self.timeout)
            return f"UDP check -- {response[1]}"
        except Exception as e:
            return f"UDP check -- {self.ip_address}:{self.port} -- Error: {e}"


class Echo(TCP):
    """Echo server class"""
    def __init__(self):
        super().__init__()
        self.service_type = "Echo"

    def check(self) -> str:
        """
        Run echo server check

        :returns:   status of check
        """
        try:
            response = check_echo_server(self.ip_address, self.port)
            if response[0]:
                return f"Echo server check -- {self.ip_address}:{self.port} -- {response[1]}"
            return f"Echo server check -- {self.ip_address}:{self.port} -- {response[1]}"
        except Exception as e:
            return f"Echo server check -- {self.ip_address}:{self.port} -- Error: {e}"
